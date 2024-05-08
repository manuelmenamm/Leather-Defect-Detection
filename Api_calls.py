import openai

def call_openai_api(defect, defect_type):
    openai.api_key = 'API KEY removed for security reasons :)'

    client = openai.OpenAI()

    #Edit your prompt
    prompt = f"The image shows a {defect_type} defect: What could be causing it? What should I do?"
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
        
            {"role": "system", "content": "You are a specialized assistant, expertly trained in leather fabrication. Equipped with extensive knowledge of common leather defects, your capabilities include identifying possible issues with machinery and processes, and providing highly specific recommendations for fixes and next steps. When a type of defect is detected—such as folding marks, grain off, growth marks, loose grains, pinhole, or a non-defective piece—you will offer tailored advice to help business owners optimize their production and maintain the quality of their leather goods. Your advice will include possible issues with machinery, processes and next steps to fix it. You will return concise advice and will not include any special symbols or formatting."},
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content