from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
import speech_recognition as sr
import json
from pydub import AudioSegment
from django.views.decorators.csrf import csrf_exempt
import os
import traceback
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from transformers import BertTokenizer, BertForSequenceClassification
from .forms import ContactForm
import torch
import requests
import re
import feedparser
from sentence_transformers import SentenceTransformer
import urllib.parse
import spacy
from spacy import displacy
import wikipedia
from dotenv import load_dotenv
import logging

"""Transcription pipeline helpers.
- We lazy-load Whisper to avoid platform import issues and reduce startup time.
- We support returning either JSON (AJAX) or HTML (form POST) responses.
"""

recognizer = sr.Recognizer()
_whisper_model = None

def _get_whisper_model():
    """Load and cache Whisper model on first use. Returns None if unavailable."""
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    try:
        import whisper
        _whisper_model = whisper.load_model("small")
        return _whisper_model
    except Exception as e:
        # Do not crash server if Whisper isn't available
        print(f"[Whisper] Failed to load: {e}")
        return None

model = BertForSequenceClassification.from_pretrained('./trained_model')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Load spaCy model for NER (Named Entity Recognition)
# Attempt to load spaCy model; fallback to a blank English model if unavailable.
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    # Fallback prevents server startup failure; NER will be limited until the model is installed.
    nlp = spacy.blank("en")

load_dotenv()
logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'transcription.html')

def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_text = request.POST.get('message')
        # Save to database via ContactForm if needed; for now, acknowledge:
        messages.success(request, 'Thank you! Your message has been sent.')
        return redirect('contact')
    return render(request, 'contact.html')

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'contact_success.html')  # Or redirect
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

@csrf_exempt
def transcription_view(request):
    logger.debug("[transcription_view] method=%s headers=%s", request.method, dict(request.headers))
    if request.method == "POST":
        logger.info("[transcription_view] POST received")
        uploaded_file = request.FILES.get("audio_file")
        user_text = request.POST.get("text_input", "").strip()

        if uploaded_file:
            logger.debug("[transcription_view] saving upload filename=%s", uploaded_file.name)
            # Ensure media directory exists
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            file_name = uploaded_file.name
            temp_input_path = os.path.join(settings.MEDIA_ROOT, file_name)
            with open(temp_input_path, "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            try:
                converted_path = convert_to_wav(temp_input_path)
            except Exception as e:
                traceback.print_exc()
                error = f"Conversion failed: {str(e)}"
                logger.error("[transcription_view] convert_to_wav failed: %s", error)
                return _transcription_response(request, error=error)

            try:
                lang_code = detect_language_whisper(converted_path)
                print("Language code passed:", lang_code)
            except Exception as e:
                traceback.print_exc()
                error = f"Language detection failed: {str(e)}"
                logger.error("[transcription_view] detect_language failed: %s", error)
                return _transcription_response(request, error=error)

            try:
                transcription = transcribe_with_whisper(converted_path)
            except Exception as e:
                traceback.print_exc()
                error = f"Transcription failed: {str(e)}"
                logger.error("[transcription_view] transcribe failed: %s", error)
                return _transcription_response(request, error=error)

            return _transcription_response(request, transcription=transcription)

        logger.warning("[transcription_view] no input provided")
        return _transcription_response(request, error="No input provided")

    print("GET request: rendering template.")
    return render(request, "transcription.html")

def convert_to_wav(input_path):
    """Converts any audio/video file to a proper PCM WAV format next to input path."""
    base, _ = os.path.splitext(input_path)
    output_path = base + ".wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)  # 16-bit mono
    audio.export(output_path, format="wav")
    return output_path

def detect_language_whisper(audio_path):
    """Detects language using Whisper. Returns 'unknown' if model not available."""
    wm = _get_whisper_model()
    if wm is None:
        return "unknown"
    import whisper
    audio = whisper.load_audio(audio_path)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(wm.device)
    _, probs = wm.detect_language(mel)
    lang_code = max(probs, key=probs.get)
    return lang_code  # Return the Whisper detected language code

def transcribe_with_whisper(audio_path):
    """Transcribe audio using Whisper. Raises RuntimeError if model unavailable."""
    wm = _get_whisper_model()
    if wm is None:
        raise RuntimeError("Whisper model is unavailable on this platform.")
    result = wm.transcribe(audio_path)
    return result.get("text", "")

def _transcription_response(request, transcription=None, error=None):
    """Return JSON for AJAX or render HTML for form post/normal requests."""
    accept = request.headers.get("accept", "")
    content_type = request.headers.get("content-type", "")
    # Check if request wants JSON (AJAX/fetch requests)
    wants_json = (
        "application/json" in accept or 
        request.headers.get("x-requested-with") == "XMLHttpRequest" or
        "multipart/form-data" in content_type  # File uploads via fetch should get JSON
    )
    if wants_json:
        if error:
            return JsonResponse({"error": error}, status=400)
        return JsonResponse({"status": "success", "transcription": transcription})
    # HTML response
    context = {}
    if transcription:
        context["transcription"] = transcription
    if error:
        context["error"] = error
    return render(request, "transcription.html", context)

@csrf_exempt
def classify_text(request):
    print("REACHED HERE")
    if request.method == 'POST':
        try:
            # Log request metadata for debugging
            logger.info("[classify_text] POST received headers=%s", dict(request.headers))
            body_raw = request.body.decode('utf-8', errors='ignore')
            logger.debug("[classify_text] body=%s", body_raw)
            data = json.loads(request.body.decode('utf-8'))
            text = data.get('message', '')

            if not text:
                logger.warning("[classify_text] missing text in request body")
                return JsonResponse({'error': 'Text is required'}, status=400)

            # BERT Classification (Determine whether the text is a Fact or News)
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            outputs = model(**inputs)
            prediction = torch.argmax(outputs.logits, dim=-1)
            label = "Fact" if prediction.item() == 0 else "News"

            # Extract entities from the input text using spaCy for better clarity
            entities = extract_entities(text)

            # Fetch Wikipedia summary based on the main query or top entity
            wikipedia_summary = get_wikipedia_summary(text)  # Fetch Wikipedia summary based on query

            # Prepare Groq client and log message
            groq_key = os.getenv('GROQ_API_KEY')
            if not groq_key:
                logger.error("[classify_text] GROQ_API_KEY is not set in environment")
                return JsonResponse({'error': 'Server is not configured with Groq API key.'}, status=500)
            try:
                from groq import Groq
            except Exception as ie:
                logger.exception("[classify_text] Groq SDK import failed: %s", ie)
                return JsonResponse({'error': 'Groq SDK not installed on the server.'}, status=500)
            client = Groq(api_key=groq_key)
            groq_model = "llama-3.1-8b-instant"
            logger.info("[classify_text] message received; predicted_label_pre=%s", label)
            # If Fact: Directly use LLaMA for fact verification
            if label == "Fact":
                payload = {
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are an expert fact checker with access to your training data and knowledge base. "
                                "Respond ONLY in this strict JSON format:\n"
                                "{\n"
                                "  \"is_true\": true or false or null,\n"
                                "  \"confidence\": number between 0 and 100,\n"
                                "  \"explanation\": \"Your explanation here.\"\n"
                                "}\n\n"
                                "INSTRUCTIONS:\n"
                                "1. First, try to verify the statement using your own training data and knowledge base.\n"
                                "2. If you have sufficient information from your training data, provide a confident assessment (true/false) with appropriate confidence score.\n"
                                "3. If you cannot determine the accuracy with certainty even after checking your knowledge base, set:\n"
                                "   - \"is_true\": null\n"
                                "   - \"confidence\": 100\n"
                                "   - \"explanation\": \"I don't know. [Explain why you cannot determine this]\"\n"
                                "4. NEVER return undefined values. Always use true, false, or null for is_true.\n"
                                "5. Be honest about uncertainty - it's better to say 'I don't know' than to guess.\n"
                                "Do not include any additional text, emojis, or commentary outside the JSON."
                            )
                        },
                        {
                            "role": "user",
                            "content": f"Check the accuracy of the following statement: {text}\n\n"
                                       
                        }
                    ]
                }

                logger.debug("[classify_text] calling Groq for Fact model=%s", groq_model)
                try:
                    response = client.chat.completions.create(
                        model=groq_model,
                        messages=payload["messages"],
                        temperature=0.2,
                    )
                    content = response.choices[0].message.content
                    try:
                        fact_data = json.loads(content)
                        explanation = fact_data.get('explanation', 'No explanation provided.')
                        is_true = fact_data.get('is_true')
                        confidence = fact_data.get('confidence', 0)
                        
                        # Ensure is_true is never undefined - convert to None if missing
                        if is_true not in [True, False, None]:
                            is_true = None
                            if confidence == 0:
                                confidence = 100
                            if explanation == 'No explanation provided.':
                                explanation = "I don't know. Unable to verify this statement with available information."

                        return JsonResponse({
                            'prediction': 'Fact',
                            'is_true': is_true,
                            'confidence': confidence,
                            'explanation': explanation,
                        })
                    except Exception as e:
                        logger.exception("[classify_text] parse error for Fact response: %s", e)
                        return JsonResponse({
                            'prediction': 'Fact',
                            'is_true': None,
                            'confidence': 100,
                            'explanation': f"I don't know. Failed to parse the fact-checking response: {str(e)}",
                        })
                except Exception as e:
                    logger.exception("[classify_text] Groq call failed for Fact: %s", e)
                    return JsonResponse({'error': 'Failed to verify fact via Groq model.'}, status=500)

            else:
                # NEWS CASE — Fetch articles based on named entities with retry mechanism
                articles = []
                max_retries = 3
                retry_count = 0
                
                # Try different search strategies
                search_queries = []
                
                # Strategy 1: Use named entities
                if entities:
                    for entity in entities:
                        search_queries.append(entity['text'])
                
                # Strategy 2: Use full text
                search_queries.append(text)
                
                # Strategy 3: Extract key words (if no entities found)
                if not entities:
                    words = text.split()
                    # Use first 3-5 meaningful words
                    key_words = [w for w in words if len(w) > 3][:5]
                    if key_words:
                        search_queries.append(' '.join(key_words))
                
                logger.info(f"[classify_text] Search strategies: {search_queries}")
                
                while retry_count < max_retries and not articles:
                    retry_count += 1
                    logger.info(f"[classify_text] Fetching news articles - Attempt {retry_count}/{max_retries}")
                    
                    # Try each search query
                    for query in search_queries:
                        if articles:
                            break  # Stop if we found articles
                        
                        # Try Google News RSS
                        rss_feed_url = f'https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en&gl=US&ceid=US:en'
                        logger.info(f"[classify_text] Trying query: '{query}' with URL: {rss_feed_url}")
                        articles += get_relevant_articles(query, rss_feed_url)
                        
                        if articles:
                            logger.info(f"[classify_text] Found {len(articles)} articles for query: '{query}'")
                    
                    # If still no articles and not the last retry, wait before retrying
                    if not articles and retry_count < max_retries:
                        import time
                        logger.info(f"[classify_text] No articles found, waiting before retry...")
                        time.sleep(2)  # Wait 2 seconds before retry

                if not articles:
                    logger.warning(f"[classify_text] No articles found after {max_retries} retries")
                    logger.warning(f"[classify_text] Tried queries: {search_queries}")
                    return JsonResponse({
                        "prediction": "News",
                        "message": "No relevant information found. Please try again later or rephrase your query.",
                        'entities': entities,
                        'retries_attempted': retry_count,
                        'debug_queries': search_queries  # For debugging
                    })

                # Select the top 5 relevant articles (or any limit you want)
                selected_articles = articles[:10]
                logger.info(f"[classify_text] Selected {len(selected_articles)} articles for analysis")

                # 🧠 Now send the selected articles to LLaMA for checking
                article_details = "\n".join(
                    [f"Title: {clean_html(article.get('title', 'No title'))}\nSummary: {clean_html(article.get('summary', 'No summary'))}" for article in selected_articles]
                )
                logger.debug(f"[classify_text] Article details length: {len(article_details)} chars")
                print("[DEBUG] Article details:")
                print(article_details[:500] + "..." if len(article_details) > 500 else article_details)
                payload = {
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are an expert fact checker with access to both provided sources and your own training data. "
                                "Analyze the information and provide your confident assessment. "
                                "Respond ONLY in this strict JSON format:\n"
                                "{\n"
                                "  \"is_true\": true or false or null,\n"
                                "  \"confidence\": number between 0 and 100,\n"
                                "  \"explanation\": \"Your explanation here. Be confident in your judgment. Provide the reasoning for your assessment.\"\n"
                                "}\n\n"
                                "INSTRUCTIONS:\n"
                                "1. First, analyze the provided articles and Wikipedia summary.\n"
                                "2. If the provided data is insufficient, use your own training data and knowledge base to verify.\n"
                                "3. If you have enough information (from articles, Wikipedia, or your knowledge), provide a confident answer (true/false) with appropriate confidence score.\n"
                                "4. If you cannot determine the accuracy even after checking all sources including your knowledge base, set:\n"
                                "   - \"is_true\": null\n"
                                "   - \"confidence\": 100\n"
                                "   - \"explanation\": \"I don't know. [Explain what information is missing or why you cannot verify this]\"\n"
                                "5. NEVER return undefined values. Always use true, false, or null for is_true.\n"
                                "6. Be honest about uncertainty - saying 'I don't know' is better than providing unreliable information.\n"
                                "7. Do not mention 'articles' or 'Wikipedia' in your explanation - present your findings as your own assessment.\n"
                                "Do not include any additional text, emojis, or commentary outside the JSON."
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Evaluate the accuracy of the following statement:\n\n"
                                f"Statement: {text}\n\n"
                                f"Here are some related articles:\n{article_details}\n\n"
                                f"Here is some relevant background information:\n{wikipedia_summary}\n\n"
                                "Based on all available information (including your own knowledge base if needed), "
                                "provide your assessment. Make your own conclusion based on all sources. "
                                "Provide a confident result or clearly state if you cannot determine the accuracy."
                            )
                        }
                    ]
                }

                logger.debug("[classify_text] calling Groq for News; articles=%d model=%s", len(selected_articles), groq_model)
                try:
                    response = client.chat.completions.create(
                        model=groq_model,
                        messages=payload["messages"],
                        temperature=0.2,
                    )
                    content = response.choices[0].message.content
                    try:
                        fact_data = json.loads(content)
                        explanation = fact_data.get('explanation', 'No explanation provided.')
                        is_true = fact_data.get('is_true')
                        confidence = fact_data.get('confidence', 0)
                        
                        # Ensure is_true is never undefined - convert to None if missing
                        if is_true not in [True, False, None]:
                            is_true = None
                            if confidence == 0:
                                confidence = 100
                            if explanation == 'No explanation provided.':
                                explanation = "I don't know. Unable to verify this statement with available information."

                        return JsonResponse({
                            'prediction': 'News',
                            'is_true': is_true,
                            'confidence': confidence,
                            'explanation': explanation,
                        })
                    except Exception as e:
                        logger.exception("[classify_text] parse error for News response: %s", e)
                        return JsonResponse({
                            'prediction': 'News',
                            'is_true': None,
                            'confidence': 100,
                            'explanation': f"I don't know. Failed to parse the fact-checking response: {str(e)}",
                        })
                except Exception as e:
                    logger.exception("[classify_text] Groq call failed for News: %s", e)
                    return JsonResponse({'error': 'Failed to verify news via Groq model.'}, status=500)

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    return HttpResponseBadRequest("Only POST method is allowed.")


def get_relevant_articles(query, rss_feed_url, timeout=10):
    """Fetch and filter articles based on query with timeout and error handling."""
    try:
        # Add headers to mimic a browser request
        import socket
        socket.setdefaulttimeout(timeout)
        
        # Parse the feed with feedparser
        feed = feedparser.parse(rss_feed_url, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        relevant_articles = []
        
        # Check if feed was successfully parsed
        if hasattr(feed, 'bozo_exception'):
            logger.warning(f"[get_relevant_articles] Feed parse warning for '{query}': {feed.bozo_exception}")
        
        if 'entries' in feed and feed.entries:
            logger.info(f"[get_relevant_articles] Found {len(feed.entries)} entries for query '{query}'")
            for e in feed.entries[:5]:
                # Ensure we have at least a title
                if hasattr(e, 'title') and e.title:
                    relevant_articles.append(e)
                    logger.debug(f"[get_relevant_articles] Added article: {e.title[:50]}...")
        else:
            logger.warning(f"[get_relevant_articles] No entries found in feed for query '{query}'")
            # Log feed status for debugging
            if hasattr(feed, 'status'):
                logger.warning(f"[get_relevant_articles] Feed status: {feed.status}")
        
        logger.info(f"[get_relevant_articles] query='{query}' rss_entries={len(getattr(feed, 'entries', []))} returned={len(relevant_articles)}")
        return relevant_articles
        
    except Exception as e:
        logger.error(f"[get_relevant_articles] Error fetching articles for query '{query}': {str(e)}")
        logger.exception(e)
        return []


def clean_html(raw_html):
    """Remove HTML tags from summary text."""
    clean_text = re.sub('<.*?>', '', raw_html)
    return clean_text.strip()

def extract_entities(text):
    """Extract named entities from the given text using spaCy."""
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append({'text': ent.text, 'label': ent.label_})
    return entities

def get_wikipedia_summary(query):
    """Fetch a relevant Wikipedia summary based on the query."""
    try:
        # Search for the page related to the query
        page = wikipedia.page(query)
        summary = page.summary  # This is a short summary of the page
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        # If there are multiple possibilities, take the first one
        return wikipedia.page(e.options[0]).summary
    except wikipedia.exceptions.HTTPTimeoutError:
        return "Wikipedia request timed out."
    except wikipedia.exceptions.RedirectError:
        return "Redirect error occurred while fetching Wikipedia page."
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found for the query."
    except Exception as e:
        return str(e)