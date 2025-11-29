// Minimal interactivity: sidebar active link, chat send + classify API
(function(){
  const navLinks = document.querySelectorAll('.nav a');
  navLinks.forEach(a => {
    if (a.href === window.location.href) a.classList.add('active');
  });

  const chatForm = document.querySelector('#chat-form');
  const messages = document.querySelector('.chat-messages');
  const input = document.querySelector('#chat-input');
  const uploadBtn = document.querySelector('#upload-btn');
  const uploadDropdown = document.querySelector('#upload-dropdown');
  const fileAudio = document.querySelector('#file-audio');
  const fileVideo = document.querySelector('#file-video');
  const fileDoc = document.querySelector('#file-document');

  function getCSRF(){
    const name = 'csrftoken=';
    return document.cookie.split(';').map(c=>c.trim()).find(c=>c.startsWith(name))?.slice(name.length)
      || document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || '';
  }

  function appendMsg(role, html){
    const div = document.createElement('div');
    div.className = 'msg ' + (role === 'user' ? 'user' : 'assistant');
    div.innerHTML = `<div class="meta">${role === 'user' ? 'You' : 'Assistant'}</div><div class="bubble">${html}</div>`;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  if (chatForm) {
    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      appendMsg('user', text);
      input.value = '';
      messages.scrollTop = messages.scrollHeight;

      // Call classify API
      console.log('[chat] Sending to /classify-text/:', text);
      fetch('/classify-text/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ message: text })
      })
      .then(async (res) => {
        const isJson = res.headers.get('content-type')?.includes('application/json');
        const data = isJson ? await res.json() : { error: 'Non-JSON response' };
        console.log('[chat] Response status:', res.status, data);
        if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
        const prediction = data.prediction || '—';
        const isTrue = typeof data.is_true === 'boolean' ? (data.is_true ? 'true' : 'false') : '—';
        const confidence = data.confidence ?? '—';
        const explanation = data.explanation || 'No explanation provided.';
        appendMsg('assistant', `<strong>${prediction}</strong><br/>is_true: ${isTrue}<br/>confidence: ${confidence}<br/>${explanation}`);
        messages.scrollTop = messages.scrollHeight;
      })
      .catch((err) => {
        console.error('[chat] Error calling classify-text:', err);
        appendMsg('assistant', `Error: ${err.message}`);
        messages.scrollTop = messages.scrollHeight;
      });
    });
  }

  // Upload dropdown behavior
  if (uploadBtn && uploadDropdown) {
    uploadBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isHidden = uploadDropdown.hasAttribute('hidden');
      if (isHidden) {
        uploadDropdown.removeAttribute('hidden');
        uploadBtn.setAttribute('aria-expanded', 'true');
      } else {
        uploadDropdown.setAttribute('hidden','');
        uploadBtn.setAttribute('aria-expanded','false');
      }
    });
    document.addEventListener('click', (e) => {
      if (!uploadDropdown.contains(e.target) && e.target !== uploadBtn && !uploadBtn.contains(e.target)) {
        uploadDropdown.setAttribute('hidden','');
        uploadBtn.setAttribute('aria-expanded','false');
      }
    });

    uploadDropdown.addEventListener('click', (e) => {
      const btn = e.target.closest('.dropdown-item');
      if (!btn) return;
      const kind = btn.dataset.kind;
      uploadDropdown.setAttribute('hidden','');
      uploadBtn.setAttribute('aria-expanded','false');
      if (kind === 'audio') fileAudio?.click();
      if (kind === 'video') fileVideo?.click();
      if (kind === 'document') fileDoc?.click();
    });
  }

  async function uploadMedia(file) {
    appendMsg('user', `📎 ${file.name}`);
    const form = new FormData();
    form.append('audio_file', file);
    console.log('[chat] Uploading media to /detect', file.name, file.type);
    const res = await fetch('/detect/', {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json',
        'X-CSRFToken': getCSRF(),
      },
      body: form
    });
    const isJson = res.headers.get('content-type')?.includes('application/json');
    const data = isJson ? await res.json() : { error: await res.text() };
    console.log('[chat] /detect response', res.status, data);
    if (!res.ok || data.error) {
      appendMsg('assistant', `Upload failed: ${data.error || ('HTTP ' + res.status)}`);
      return;
    }
    // Expect { status: 'success', transcription: '...' }
    if (data.transcription) {
      appendMsg('assistant', `Transcript: ${data.transcription}`);
    } else {
      appendMsg('assistant', 'Upload complete.');
    }
  }

  fileAudio?.addEventListener('change', () => {
    const f = fileAudio.files?.[0];
    if (f) uploadMedia(f);
    fileAudio.value = '';
  });
  fileVideo?.addEventListener('change', () => {
    const f = fileVideo.files?.[0];
    if (f) uploadMedia(f);
    fileVideo.value = '';
  });
  fileDoc?.addEventListener('change', () => {
    const f = fileDoc.files?.[0];
    if (!f) return;
    appendMsg('user', `📎 ${f.name}`);
    // Document processing not implemented server-side; just acknowledge.
    appendMsg('assistant', 'Document attached. (Processing not yet supported.)');
    fileDoc.value = '';
  });
})();
