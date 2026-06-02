from app import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True agar server otomatis restart kalau kita save file
    app.run(debug=True)