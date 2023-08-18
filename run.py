from main import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='172.31.13.106', debug=True, port=5000)