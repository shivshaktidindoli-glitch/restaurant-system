import os
import rjsmin

def minify_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        js = f.read()
    
    minified = rjsmin.jsmin(js)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(minified)
        
    print(f"Minified {input_path} to {output_path}")
    print(f"Original size: {len(js)} bytes")
    print(f"Minified size: {len(minified)} bytes")

if __name__ == '__main__':
    minify_file('static/js/customer.js', 'static/js/customer.min.js')
