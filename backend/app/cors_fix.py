with open("__init__.py", "r") as f:
    content = f.read()

new_content = content.replace("    CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)", "    CORS(app, resources={r'/*': {'origins': 'https://kardosa.xyz'}}, supports_credentials=True)")
new_content = new_content.replace("response.headers['Access-Control-Allow-Origin'] = '*'", "response.headers['Access-Control-Allow-Origin'] = 'https://kardosa.xyz'")

with open("__init__.py", "w") as f:
    f.write(new_content)

print("CORS configuration updated successfully!")
