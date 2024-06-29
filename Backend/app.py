from flask import Flask, request, jsonify
from dotenv import load_dotenv
import base64
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai
from flask_cors import CORS

app = Flask(__name__)
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

CORS(app) 

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    images = pdf2image.convert_from_bytes(uploaded_file.read())
    first_page = images[0]

    img_byte_arr = io.BytesIO()
    first_page.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    pdf_parts = [
        {
            "mime_type": "image/jpeg",
            "data": base64.b64encode(img_byte_arr).decode()
        }
    ]
    return pdf_parts

@app.route('/api/evaluate_resume', methods=['POST'])
def evaluate_resume():
    input_text = request.form['job_description']
    prompt_type = request.form['prompt_type']
    uploaded_file = request.files['resume']

    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400

    pdf_content = input_pdf_setup(uploaded_file)
    
    if prompt_type == "evaluation":
         prompt = """
         You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
         Please provide a detailed professional evaluation on whether the candidate's profile aligns with the role. 
         Your evaluation should cover the following points:

         1. **Overall Fit**: Does the candidate's experience and skills match the job requirements?
         2. **Strengths**: Highlight the key strengths and qualifications of the candidate in relation to the job.
         3. **Weaknesses**: Identify any gaps or areas where the candidate's profile does not meet the job requirements.
         4. **Missing Keywords**: List any important keywords or skills from the job description that are missing from the resume.
         5. **Recommendations**: Provide any recommendations for the candidate to improve their profile for this role.

         Please ensure your evaluation is thorough and professional.
         """

    elif prompt_type == "percentage_match":
        prompt = """
        You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of full stack web development and ATS functionality, 
        your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
        the job description. First the output should come as percentage and then keywords missing and last final thoughts.
        """
    else:
        return jsonify({"error": "Invalid prompt type"}), 400

    response = get_gemini_response(input_text, pdf_content, prompt)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
