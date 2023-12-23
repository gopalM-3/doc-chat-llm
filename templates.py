CSS = '''
<style>
    .chat-container {
        max-width: 400px;
        margin: 20px auto;
        border: 1px solid #ccc;
        border-radius: 8px;
        overflow: hidden;
    }

    .chat-bubble {
        padding: 10px;
        margin: 5px;
        border-radius: 8px;
        clear: both;
        word-wrap: break-word;
    }

    .user-bubble {
        background-color: #007bff;
        color: #fff;
        float: right;
    }

    .bot-bubble {
        background-color: #eee;
        color: #333;
        float: left;
    }
</style>
'''

user_template = '''
    <div class='chat-bubble user-bubble'>
        {{message}}
    </div>
    '''

bot_template = '''
    <div class='chat-bubble bot-bubble'>
        {{message}}
    </div>
    '''
