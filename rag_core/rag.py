import numpy as np
import os
import re
import torch

from PyPDF2 import PdfReader
from dotenv import load_dotenv
from google import genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from scipy.spatial.distance import cosine
from transformers import AutoTokenizer, AutoModel

from rag_core.tools import tools


def context_base(file, file_name):
    load_dotenv()
    text = ""
    pdfreader = PdfReader(file)

    for page in pdfreader.pages:
        text += page.extract_text()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=7000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

    big_chunks = splitter.split_text(text)

    print(f"File import succeeded. Original text split into {len(big_chunks)} chunks.")

    api = os.getenv("api_key")
    client = genai.Client(api_key = os.getenv("api_key"))

    chunks = []
    for i, chunk in enumerate(big_chunks):
        print(f"Processing chunk {i+1}/{len(big_chunks)} (length: {len(chunk)} characters)...")

        prompt = f"""Split the following text into meaningful segments with less than 300 words without alternating any original wording,
        where each segment represents a distinct chapter, major section, or a cohesive logical unit.
        Ensure all content from the original document is covered in a segment.
        Put ********** between each segment and at the top of your response and include a concise title for each segment:

        text: {chunk}
        """

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20", contents= prompt
            )

            if response.candidates and response.candidates[0].content.parts:
                segment_text = response.candidates[0].content.parts[0].text
                chunks.append(f"--- Segment from Chunk {i+1} ---\n{segment_text}\n")
                print(f"  Generated {response.usage_metadata.candidates_token_count} tokens for chunk {i+1}")
            else:
                print(f"  No content generated for chunk {i+1}. Finish reason: {response.candidates[0].finish_reason if response.candidates else 'N/A'}")
                print(f"  Full response for chunk {i+1}: {response}")

        except Exception as e:
            print(f"  An error occurred processing chunk {i+1}: {e}")

    final_segmented_document = "\n".join(chunks)

    ai_chunks = final_segmented_document.split('**********')

    pattern = r"\.{5}\.+"
    cleaned_chunks = [re.sub(pattern, '', t) for t in ai_chunks]
    print(f"Text cleaned successfully. {len(cleaned_chunks)} segments generated.")

    model_name = "ibm-granite/granite-embedding-278m-multilingual"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    batch_size = 200
    embeddings_np = []
    for i in range(0, len(cleaned_chunks), batch_size):
        batch = cleaned_chunks[i:i+batch_size]
        inputs = tokenizer(batch, padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
        batch_embeddings = outputs.last_hidden_state.mean(dim=1)
        batch_embeddings_np = batch_embeddings.numpy()
        embeddings_np.extend(batch_embeddings_np)
        print('batch processed')
    print('Embeddings generated successfully.')

    database = tools.sqlserver()
    database.insert(cleaned_chunks, embeddings_np, file_name)

    response = f"Database updated successfully with file: {file_name}"
    return response

def file_deletion(file_name):
    database = tools.sqlserver()
    response = database.delete(file_name)

    return response

def response_generation(query):
    print(f"Received query: {query}")
    database = tools.sqlserver()
    print('Retrieving data from sqlite database...')
    cleaned_chunks, embeddings_np, file_name_list = database.retrieval()
    print('Data retrieved from sqlite database successfully.')

    print(len(cleaned_chunks), len(embeddings_np), len(file_name_list))
    if len(cleaned_chunks) != len(embeddings_np):
        raise ValueError("The number of cleaned chunks does not match the number of embeddings.")
    print(f"Loaded {len(cleaned_chunks)} chunks and {len(embeddings_np)} embeddings from database.")

    model_name = "ibm-granite/granite-embedding-278m-multilingual"
    print('Loading model...')
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print('Tokenizer loaded successfully.')
    model = AutoModel.from_pretrained(model_name)
    print('Model loaded successfully.')

    query_inputs = tokenizer(query, padding=True, truncation=False, return_tensors="pt")
    print('Query tokenized successfully.')

    with torch.no_grad():
        query_outputs = model(**query_inputs)
    print('Query processed successfully.')

    query_embeddings = query_outputs.last_hidden_state.mean(dim=1)
    query_embeddings_np = query_embeddings.numpy()
    print('Query embedding generated successfully.')

    similarities = []
    for embed in embeddings_np:
        similarity = 1-cosine(embed, query_embeddings_np[0])
        similarities.append(similarity)
    print('Similarities calculated successfully.')


    print(f"Text cleaned successfully.")
    print(len(similarities), len(cleaned_chunks), len(embeddings_np))

    bundle = []
    for i in range(len(similarities)):
        bundle.append((i, similarities[i], cleaned_chunks[i], file_name_list[i]))
    print('Bundle created successfully.')

    def airc(tup):
        return tup[1]

    bundle.sort(key=airc, reverse=True)

    context = [(a[0], a[2], a[3]) for a in bundle[:7]]
    print('Context created successfully.')

    prompt = f"""
    You are a helpful AI assistant that answers questions based on the provided context.

    Rules:
    1. Only use information from the provided context to answer questions
    2. If the context doesn't contain enough information, say so honestly
    3. Be specific and cite relevant parts of the context
    4. Keep your answers clear and concise
    5. If you're unsure, admit it rather than guessing
    6. If there are typing mistakes in the question, tell the user to correct it instead of answering the question
    7. Answer in the language of the question
    8. At the end of your answer, list the source file names and section number you used to construct your answer in the format: (file_name, section_number), (file_name, section_number), ...

    Context:
    {context}

    Question: {query}

    Answer based on the context above:
    """
    print('Prompt created successfully.')

    api = os.getenv("api_key")
    client = genai.Client(api_key = os.getenv("api_key"))

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-05-20", contents= prompt
    )
    print('Response generated successfully.')

    return (response.text, context)
