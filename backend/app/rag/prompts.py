"""
Prompt templates for AyurPedia RAG system.
"""

from langchain_core.prompts import PromptTemplate


# Classification prompt for formulation categorization
CLASSIFICATION_PROMPT = PromptTemplate(
    input_variables=["formulation_description"],
    template="""You are an expert in Indian pharmaceutical and traditional medicine regulations. 
Classify the following formulation into one of these categories:

Categories:
1. Classical - Traditional Ayurvedic formulations from classical texts (e.g., Chyawanprash, Triphala)
2. Proprietary - New formulations with patent potential or novel combinations
3. Ayurveda-Aahar - Food products containing Ayurvedic herbs listed in Schedule A
4. Cosmetic - Products for external application with cosmetic benefits
5. Phytopharmaceutical - Plant-derived pharmaceutical products
6. Nutraceutical - Dietary supplements with health benefits
7. Unknown - Cannot classify based on description

Formulation Description: {formulation_description}

Provide your response in this format:
Category: [category name]
Confidence: [0.0-1.0]
Relevant Laws: [list of relevant laws]
Description: [brief explanation of classification]
"""
)


# Language name mapping helper
LANGUAGE_MAP = {
    'hi': 'Hindi (हिंदी)',
    'ta': 'Tamil (தமிழ்)',
    'te': 'Telugu (తెలుగు)',
    'bn': 'Bengali (বাংলা)',
    'mr': 'Marathi (मराठी)',
    'gu': 'Gujarati (ગુજરાતી)',
    'kn': 'Kannada (ಕನ್ನಡ)',
    'ml': 'Malayalam (മലയാളം)',
    'pa': 'Punjabi (ਪੰਜਾਬੀ)',
    'or': 'Odia (ଓଡ଼ିଆ)',
    'sa': 'Sanskrit (संस्कृतम्)',
    'en': 'English'
}

# RAG prompt for comprehensive answer generation with citations and multilingual Gemini support
RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question", "target_language"],
    template="""You are AyurPedia's Lead Legal & Regulatory AI Consultant, an expert in Indian and International Intellectual Property Rights (IPR), Patent Law (The Patents Act, 1970), the Biological Diversity Act, 2002, FSSAI Ayurveda-Aahar Regulations 2022, Traditional Knowledge Digital Library (TKDL), and the WIPO GRATK Treaty, 2024.

Analyze the user's question and provide a comprehensive, well-structured, thorough, and highly informative answer.

### Retrieved Statutory Legal Context:
{context}

### User's Inquiry:
{question}

### Target Output Language:
{target_language}

### Instructions for Generating Your Answer:
1. **Thorough & Complete Explanation**:
   - Provide a detailed, informative, and practical explanation answering all aspects of the user's inquiry.
   - For conceptual inquiries (e.g. "what is a patent?", "what is IPR?", "what is Section 3(p)?"), provide the complete legal definition, foundational patent criteria (Novelty, Inventive Step, Industrial Applicability), statutory framework, and its direct relevance/impact on Ayurvedic formulations and Traditional Knowledge.
   - If the user asks about formulations or patentability, explain how Section 3(p) restricts patenting traditional knowledge/admixtures, what constitutes patentable novel synergy, and when National Biodiversity Authority (NBA) approval is required.
2. **Grounding & Accurate Citations**:
   - Attribute specific legal statutory provisions, sections, and definitions to the provided context using the citation format: `[Source: Document Name, Section: Section Name/Number]` (e.g., `[Source: Patents Act 1970, Section: 2(1)(m)]` or `[Source: Patents Act 1970, Section: 3(p)]` or `[Source: Biological Diversity Act 2002, Section: 6]`).
   - Do NOT invent false section numbers. Use the exact section references from the context where available.
3. **Professional & Structured Formatting**:
   - Use bold headers, bullet points, and numbered lists for readability.
   - Include key takeaways and practical guidance for Ayurvedic practitioners, innovators, and pharmaceutical researchers.
4. **Multilingual Response**:
   - If the Target Output Language is NOT English, output the entire response, explanations, and headings in **{target_language}** using its native script with fluent, natural phrasing. Keep the citation tag brackets in recognizable format like `[Source: Patents Act 1970, Section: 3(p)]`.

### Response:"""
)


# Validation prompt for checking citation validity
VALIDATION_PROMPT = PromptTemplate(
    input_variables=["response", "retrieved_docs"],
    template="""You are a citation validator. Check if the following response properly cites the 
retrieved documents.

Response:
{response}

Retrieved Documents:
{retrieved_docs}

Instructions:
1. Check if each claim in the response has a corresponding citation
2. Verify that citations match the retrieved documents
3. Identify any uncited claims
4. Return your assessment in this format:
   - All claims cited: [Yes/No]
   - Citations match documents: [Yes/No]
   - Uncited claims: [list of uncited claims if any]
   - Overall validity: [Valid/Invalid]
"""
)


# Abstention prompt for out-of-scope refusal
ABSTENTION_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="""You are a legal expert specializing in Indian and international intellectual property law. 
The user has asked a question that is outside the scope of the available legal documents.

Question: {question}

Instructions:
1. Politely refuse to answer the question
2. Explain that the question is outside the scope of available legal documents
3. Suggest what topics you can help with (IP law, traditional knowledge, genetic resources, etc.)
4. Do not provide any legal advice or make claims without proper documentation

Response:"""
)


# Confidence scoring prompt
CONFIDENCE_PROMPT = PromptTemplate(
    input_variables=["response", "retrieved_scores"],
    template="""You are a confidence evaluator. Assess the confidence level of the following response 
based on the retrieval similarity scores.

Response:
{response}

Retrieval Similarity Scores:
{retrieved_scores}

Instructions:
1. Evaluate the overall confidence based on:
   - Average similarity score of retrieved documents
   - Number of relevant documents retrieved
   - Clarity and specificity of the response
2. Return confidence level: High, Medium, or Low
3. Provide a brief justification

Confidence Assessment:"""
)
