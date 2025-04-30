from uuid import uuid4
from flask import Flask, request, jsonify
from agent import get_agent


app = Flask(__name__)
agent = get_agent()

@app.route('/query', methods=['POST'])
def query_llm():
    try:
        # Get the input message from the request
        data = request.json
        input_message = data.get('message', '')
        thread_id = data.get('thread_id', uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        if not input_message:
            return jsonify({'error': 'Message is required'}), 400

        # Query the LLM model
        response = agent.invoke( {"messages": [{"role": "user", "content": input_message}]},
                                stream_mode="values",
                                config=config)

        # Return the response
        return jsonify({'response': response["messages"][-1].content, 'thread_id': thread_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)