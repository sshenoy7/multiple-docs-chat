css = '''
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: rgb(241 245 249)
}
.chat-message.bot {
    background-color: rgb(248 250 252)
}
.chat-message .avatar {
  width: 20%;
}
.chat-message .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 80%;
  padding: 0 1.5rem;
  color: rgb(3 7 18);
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://ih1.redbubble.net/image.345993101.2884/bg,f8f8f8-flat,750x,075,f-pad,750x1000,f8f8f8.u2.jpg">
    </div>
    <div class="message">{{MSG}}</div>
    <div style="clear:both;"></div> <!-- Add a clear fix to prevent any elements from wrapping -->
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://e7.pngegg.com/pngimages/284/947/png-clipart-smiley-desktop-happiness-face-smiley-miscellaneous-face-thumbnail.png">
    </div>    
    <div class="message">{{MSG}}</div>
    <div style="clear:both;"></div> <!-- Add a clear fix to prevent any elements from wrapping -->
</div>
'''