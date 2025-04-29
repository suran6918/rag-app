from flask import Flask, request, jsonify
from langchaingraph import get_graph

app = Flask(__name__)
mymodel = get_graph()

@app.route('/query', methods=['POST'])
def query_llm():
    try:
        # Get the input message from the request
        data = request.json
        input_message = data.get('message', '')
        

        if not input_message:
            return jsonify({'error': 'Message is required'}), 400

        # Query the LLM model
        response = mymodel.invoke({"question": input_message})

        # Return the response
        return jsonify({'response': response["answer"]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)