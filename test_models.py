import google.generativeai as genai
genai.configure(api_key="AIzaSyA1v-nP7hvC8shSg09eyd1xDynWq201T48")
for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)