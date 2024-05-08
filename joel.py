from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def generate_review(interview_score, posture_score):
    # Logic to generate review based on interview score and posture score
    if interview_score >= 8 and posture_score >= 8:
        return "Excellent! You have shown great improvement in both your interview performance and posture. Keep up the good work!"
    elif interview_score >= 6 and posture_score >= 6:
        return "Good job! Your interview performance and posture are improving steadily. Keep practicing for better results."
    elif interview_score >= 4 and posture_score >= 4:
        return "You're making progress, but there's still room for improvement in both your interview performance and posture. Keep working on it!"
    else:
        return "There is significant room for improvement in both your interview performance and posture. Consider seeking further guidance and practice."



@app.route('/review', methods=['POST'])
def review():
    session['interview_score'] = int(request.form['interview_score'])
    session['posture_score'] = int(request.form['posture_score'])
    return redirect(url_for('analysis'))

@app.route('/analysis')
def analysis():
    if 'interview_score' not in session or 'posture_score' not in session:
        return redirect(url_for('index'))
    
    interview_score = session['interview_score']
    posture_score = session['posture_score']
    
    prev_interview_score = session.get('prev_interview_score', None)
    prev_posture_score = session.get('prev_posture_score', None)
    
    if prev_interview_score is None or prev_posture_score is None:
        session['prev_interview_score'] = interview_score
        session['prev_posture_score'] = posture_score
        return render_template('analysis.html', review=generate_review(interview_score, posture_score), prev_review=None)
    
    prev_review = generate_review(prev_interview_score, prev_posture_score)
    new_review = generate_review(interview_score, posture_score)
    
    session['prev_interview_score'] = interview_score
    session['prev_posture_score'] = posture_score
    
    return render_template('analysis.html', review=new_review, prev_review=prev_review)

if __name__ == '__main__':
    app.run(debug=True)
