from flask import Flask, request, jsonify
from flask_cors import CORS
from chroma_functions import query_documents
from openai_query import query_openai_with_chunks

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://yahyaghani.com"]}})

@app.route('/query', methods=['POST'])
def query_documents_endpoint():
    query_text = request.json.get('query_text')

    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    try:
        # Query the documents to get the chunks
        results = query_documents(query_text)
        chunk_texts = [result['chunk_text'] for result in results if result['chunk_text']]
        
        if not chunk_texts:
            return jsonify({"error": "No chunks found for the given query"}), 404

        # Get OpenAI response with the chunks
        openai_response = query_openai_with_chunks(query_text, chunk_texts)
        
        print(f"Sending response: {openai_response}")  # Debugging statement
        return jsonify({"results": openai_response}), 200
    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging statement
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
