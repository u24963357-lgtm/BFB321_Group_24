from flask import Flask, render_template

app = Flask(
    __name__,
    template_folder="Template",
    static_folder="css",
    static_url_path="/css",
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/catalogue')
def catalogue():
    return render_template('customer facing/catalogue.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('Admin Facing/dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)