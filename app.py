from flask import Flask, render_template, request, send_file, redirect, url_for
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CLEANED_FOLDER = 'cleaned'
GRAPH_FOLDER = 'static/graphs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)
os.makedirs(GRAPH_FOLDER, exist_ok=True)
df = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global df
    msg = ""
    tables = []
    graphs = []

    if request.method == 'POST':
        file = request.files['file']
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            df = pd.read_csv(file_path)
            tables = [df.head().to_html(classes='table table-bordered')]
            msg = "File uploaded successfully!"

    return render_template('index.html', tables=tables, msg=msg)

@app.route('/clean', methods=['POST'])
def clean():
    global df
    msg = ""
    if df is not None:
        if 'remove_duplicates' in request.form:
            df.drop_duplicates(inplace=True)

        option = request.form.get('missing_option')
        if option == 'mean':
            df.fillna(df.mean(numeric_only=True), inplace=True)
        elif option == 'median':
            df.fillna(df.median(numeric_only=True), inplace=True)
        elif option == 'zero':
            df.fillna(0, inplace=True)
        elif option == 'missing':
            df.fillna("Missing", inplace=True)

        cleaned_path = os.path.join(CLEANED_FOLDER, 'cleaned_file.csv')
        df.to_csv(cleaned_path, index=False)
        msg = "Data cleaned successfully!"

    return redirect(url_for('analyze', msg=msg))

@app.route('/analyze')
def analyze():
    global df
    msg = request.args.get('msg', '')
    graphs = []
    if df is not None:
        # Missing Value Heatmap
        plt.figure(figsize=(8, 4))
        sns.heatmap(df.isnull(), cbar=False)
        plt.title('Missing Value Heatmap')
        plt.tight_layout()
        plt.savefig(f'{GRAPH_FOLDER}/heatmap.png')
        graphs.append('heatmap.png')
        plt.clf()

        # Correlation Heatmap
        plt.figure(figsize=(8, 4))
        sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='coolwarm')
        plt.title('Correlation Heatmap')
        plt.tight_layout()
        plt.savefig(f'{GRAPH_FOLDER}/corr_heatmap.png')
        graphs.append('corr_heatmap.png')
        plt.clf()

        # Histogram
        plt.title('Histogram of Numerical Columns')
        df.hist(figsize=(8, 4))
        plt.tight_layout()
        plt.savefig(f'{GRAPH_FOLDER}/histogram.png')
        graphs.append('histogram.png')
        plt.clf()

        # Boxplot
        plt.figure(figsize=(8, 4))
        sns.boxplot(data=df.select_dtypes(include='number'))
        plt.xticks(rotation=45)
        plt.title('Boxplot of Numerical Columns')
        plt.tight_layout()
        plt.savefig(f'{GRAPH_FOLDER}/boxplot.png')
        graphs.append('boxplot.png')
        plt.clf()

        stats = df.describe().to_html(classes='table table-bordered')
        return render_template('index.html', tables=[df.head().to_html(classes="table table-striped")], stats=stats, graphs=graphs, download_link=True, msg=msg)
    return redirect('/')

@app.route('/download')
def download():
    cleaned_path = os.path.join(CLEANED_FOLDER, 'cleaned_file.csv')
    return send_file(cleaned_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
