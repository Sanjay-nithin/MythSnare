# # from selenium import webdriver
# # from selenium.webdriver.common.by import By
# # import pandas as pd
# # import re

# # chrome_options = webdriver.ChromeOptions()
# # chrome_options.add_experimental_option("detach", True)

# # driver = webdriver.Chrome(options=chrome_options)
# # driver.get("https://sathee.prutor.ai/article/biology/biology-amazing-facts-trivia-on-human-body/")

# # content_div = driver.find_element(By.CLASS_NAME, "content-wrapper")
# # full_text = content_div.find_elements(By.TAG_NAME, "li")

# # full_p_tags = content_div.find_elements(By.TAG_NAME, 'p')

# # p_lines = [line.text for line in full_p_tags]
# # print(p_lines[:10])
# # lines = [line.text for line in full_text]

# # lines.extend(p_lines)
# # labels = [0 for _ in range(len(lines))]


# # dictionary = {"text": lines, "label":labels}

# # data = pd.DataFrame(dictionary)
# # # print(data[:10])

# # def clean_text(text):
# #     # Remove unwanted characters but keep %, ., ?, !
# # #     text = re.sub(r"[^a-zA-Z0-9\s\.,%!?]", "", text)
# # #     text = re.sub(r"\s+", " ", text).strip()
# # #     return text

# # # data["text"] = data["text"].apply(clean_text)

# # # data.to_csv('data.csv', index=False)
# # # driver.quit()
# # import re

# # another = "1. The unit for mass is Kg (Kilograms). 2. The unit for volume is ml (millilitres). 3. The unit for length is m (meters). 4. The unit for temperature is oC (degrees centigrade). 5. An atom is a very small particle. 6. Solids have a fixed volume and shape. 7. Liquids have a fixed volume but take up the shape of the container they are in. 8. Gases take up the volume of the container they are in. 9. Density is how heavy something is for its volume. 10. The three states of matter are solid liquid and gas. 11. Malleable means it can be bent and shaped. 12. Ductile means it can be drawn out into a thin wire. 13. In a solid particles are tightly packed in rows and columns. 14. In a liquids particles are closely packed in a random arrangement. 15. In a gas particles are far apart. 16. In a solid the particles move by vibrating about a fixed position.  17. In a liquid particles move by flowing over each other.  18. In a gas, particles move very fast and in random directions.  19. All matter is made up of particles.  20. An element is made up of one type of atom.  21. The periodic table has 8 groups. 22. The rows in the periodic table are called periods. 23. The atomic number of an element is the number of protons. 24. The mass number of an element is the number of proton + neutrons. 25. In a neutral atom the number of protons = number of electrons. 26. The scientist who came up with the idea of atoms as tiny balls was John Dalton. 27. The scientist who came up with the plum pudding model was JJ Thompson.  28. The scientist who discovered the nucleus was Ernest Rutherford. 29. The scientist who came up with the idea that electrons were held in shells around the nucleus was Bohr.  30. The molecular formula for hydrogen gas is H2 31. A molecule is two or more atoms chemically bonded together 32. A compound is two or more different elements chemically bonded together.  33. Gases can be compressed 34. Atoms contain protons, neutrons and electrons 35. Protons have a positive charge 36. Neutrons have no charge 37. Electrons have a negative charge 38. Atoms have a nucleus at their centre 39. Protons and neutrons are held in the nucleus 40. Elections orbit the nucleus in shells 41. The molecular formula for oxygen gas is O2. 42. The molecular formula for methane is CH4. 43. The molecular formula for carbon dioxide is CO2. 44. The molecular formula for water is H2O. 45. The molecular formula for chlorine is Cl2. 46. The molecular formula for ammonia is NH3. 47. The test for carbon dioxide is that it turns limewater milky. 48. The test for hydrogen is it burns with a squeaky pop. 49. The test for oxygen is it relights a glowing splint. 50. The test for chlorine is it bleaches litmus paper. 51. Evidence of a chemical reaction are colour change, temp change, gas given off, sound, flame 52. Iron + sulphur -> Iron sulphide 53. Change of state from solid to liquid is called melting 54. Change of state from liquid to gas is called evaporation 55. Change of state from liquid to solid is called solidification or freezing 56. Change of state from gas to liquid is called condensing 57. Change of state from solid to gas is called sublimation 58. To cause a change of state you must add or remove energy from the particles 59. An alloy is a mixture of two or more metals 60. A mixture is made up of two or more substances not chemically bonded together 61. Acid + Alkali -> salt + water 62. The formula for hydrochloric acid is HCl 63. The formula for nitric acid is HNO3 64. The formula for sulphuric acid is H2SO4 65. The formula for potassium hydroxide is KOH 66. The formula for sodium hydroxide is NaOH 67. The metals in the middle block of the periodic table are called transition metals 68. Acid + alkali is called a neutralisation reaction 69. Acids contain H+ ions 70. Alkalis contain OH- ions 71. The metals in the middle block of the periodic table are called transition metals 72. Acid + alkali is called a neutralisation reaction 73. Acids contain H+ ions 74. Alkalis contain OH- ions 75. Acids have a pH of 1-6 76. Alkalis have a pH of 8-14 77. pH of 7 is neutral 78. Seven properties of metals are: strong, malleable, ductile, good conductor of heat, good conductor of electricity, sonorous, tough. 79. Diffusion is the movement of particles from an area of high concentration to an area of low concentration 80. Gas pressure is caused by particles colliding with the side of the container 81. The independent variable is the one you choose to change in an investigation 82. The dependent variable is the result that you measure in your investigation 83. The control variables are the ones you keep the same to ensure a fair test 84. When plotting a line graph the independent variable goes on the x axis 85. When plotting a line graph the dependent variable goes on the y axis 86. To calculate the mean you add the numbers together and divide by the number of values you have used 87. Metals are on the left hand side of the Periodic Table 88. Non metals are on the right hand side of the Periodic Table 89. Group 1 elements are often called the alkali metals because the form an alkali when they react with water 90. Group 7 elements are called the halogens  91. Group 8 elements are called the Noble gases and they are inert. 92. “Inert” means unreactive. 93. Boiling point of water is 100oC. 94. Melting point of ice is 0oC. 95. Viscosity of a liquid is how 'thick' the liquid is.  96. Acid + metal carbonate -> salt + water + carbon dioxide 97. Acid + metal -> salt + hydrogen 98. acid + metal oxide -> salt + water 99. Combustion is a chemical reaction often referred to as burning. 100. Thermal decomposition means breaking down by heating. "
# # another = "0. " + another
# # facts = re.split(r'\d+\.\s+', another)[1:]
# # facts = [fact.strip() for fact in facts if fact]

# # with open('data.csv', 'a') as file:
# #     for i in facts:
# #         file.write(f'"{i}"' + ", 0" + '\n')


# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import pandas as pd
# import re

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_experimental_option("detach", True)

# driver = webdriver.Chrome(options=chrome_options)
# driver.get("https://www.jameswebbdiscovery.com/faqs/what-are-100-space-facts")

# content_div = driver.find_element(By.CLASS_NAME, "tyJCtd mGzaTb Depvyb baZpAe")
# full_text = content_div.find_elements(By.TAG_NAME, "p")
import re
def clean_text(text):
    # Remove unwanted characters but keep %, ., ?, !
    text = re.sub(r"[^a-zA-Z0-9\s\.,%!?]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# for i in full_text[:20]:
#     print(i.text)

# driver.quit()

import pandas as pd

data = pd.read_json('./News.json', lines=True)
data["headline"] = data["headline"].apply(clean_text)
data = list(data["headline"][:1000])

with open("data.csv", 'a') as file:
    for i in data:
        file.write(f'"{i}"'+", 1" + '\n')
