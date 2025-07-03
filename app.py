from flask import Flask, render_template, request, redirect, url_for, flash
import threading, requests, random, time, os
from termcolor import cprint, colored

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global to hold thread reference
worker = None

# Core functions

def validate_token(token):
    try:
        res = requests.get(f"https://graph.facebook.com/me?access_token={token}")
        if res.status_code == 200 and 'id' in res.json(): return True
    except:
        pass
    return False


def comment_loop(post_id, comments, tokens, delay):
    count = 1
    while True:
        for token in tokens:
            comment = random.choice(comments)
            res = requests.post(f"https://graph.facebook.com/{post_id}/comments", data={
                "message": comment,
                "access_token": token
            })
            status = 'SUCCESS' if res.status_code == 200 else 'FAIL'
            ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            print(f"[{ts}] [{status}] ({token[:10]}...) -> {comment}")
            count += 1
            time.sleep(delay)


@app.route('/', methods=['GET', 'POST'])
def index():
    global worker
    if request.method == 'POST':
        post_id = request.form['post_id'].strip()
        delay = int(request.form['delay'])
        # Save uploaded files
        comments = request.files['comments']
        tokens = request.files['tokens']
        comments_path = 'comments.txt'
        tokens_path = 'tokens.txt'
        comments.save(comments_path)
        tokens.save(tokens_path)
        # Load lines
        comments_list = [l.strip() for l in open(comments_path) if l.strip()]
        tokens_list  = [l.strip() for l in open(tokens_path) if l.strip() and validate_token(l.strip())]
        if not tokens_list:
            flash('No valid tokens found', 'danger')
            return redirect(url_for('index'))
        # Start background thread
        if worker and worker.is_alive():
            flash('Bot is already running', 'warning')
        else:
            worker = threading.Thread(target=comment_loop, args=(post_id, comments_list, tokens_list, delay), daemon=True)
            worker.start()
            flash('Bot started successfully', 'success')
        return redirect(url_for('index'))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
