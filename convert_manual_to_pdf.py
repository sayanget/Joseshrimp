#!/usr/bin/env python3
"""
Script para convertir el manual de usuario de Markdown a HTML
Luego se puede convertir a PDF usando el navegador (Ctrl+P -> Guardar como PDF)
"""

import markdown2
from pathlib import Path

def convert_markdown_to_html(md_file, html_file):
    """
    Convierte un archivo Markdown a HTML con estilos profesionales
    
    Args:
        md_file: Ruta al archivo Markdown
        html_file: Ruta de salida para el HTML
    """
    print(f"Leyendo archivo Markdown: {md_file}")
    
    # Leer el contenido Markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convertir Markdown a HTML con extensiones
    print("Convirtiendo Markdown a HTML...")
    html_body = markdown2.markdown(md_content, extras=[
        'tables',
        'fenced-code-blocks',
        'header-ids',
        'toc',
        'break-on-newline',
        'code-friendly'
    ])
    
    # Crear HTML completo con estilos CSS optimizados para impresión
    full_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manual de Usuario - Sistema de Gestión de Ventas</title>
    <style>
        /* Estilos para pantalla */
        @media screen {{
            body {{
                max-width: 900px;
                margin: 40px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 40px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
        }}
        
        /* Estilos para impresión/PDF */
        @media print {{
            @page {{
                size: A4;
                margin: 2cm;
            }}
            
            body {{
                margin: 0;
                padding: 0;
            }}
            
            .container {{
                padding: 0;
            }}
            
            h1 {{
                page-break-before: always;
            }}
            
            h1:first-of-type {{
                page-break-before: auto;
            }}
            
            table, pre, blockquote {{
                page-break-inside: avoid;
            }}
            
            h1, h2, h3, h4, h5, h6 {{
                page-break-after: avoid;
            }}
        }}
        
        /* Estilos generales */
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        
        .container {{
            font-size: 11pt;
        }}
        
        /* Encabezados */
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 28pt;
        }}
        
        h1:first-of-type {{
            text-align: center;
            border-bottom: none;
            margin-top: 0;
            font-size: 36pt;
            color: #3498db;
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 20pt;
        }}
        
        h3 {{
            color: #555;
            margin-top: 25px;
            margin-bottom: 12px;
            font-size: 16pt;
        }}
        
        h4 {{
            color: #666;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 14pt;
        }}
        
        /* Párrafos y listas */
        p {{
            margin: 12px 0;
            text-align: justify;
        }}
        
        ul, ol {{
            margin: 12px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 6px 0;
        }}
        
        /* Tablas */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            font-size: 10pt;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        
        td {{
            border: 1px solid #ddd;
            padding: 10px;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        /* Código */
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', Consolas, monospace;
            font-size: 9pt;
            color: #c7254e;
        }}
        
        pre {{
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-left: 4px solid #3498db;
            padding: 15px;
            overflow-x: auto;
            border-radius: 4px;
            margin: 20px 0;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
            color: #333;
            font-size: 9pt;
        }}
        
        /* Citas */
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 20px 0;
            color: #666;
            font-style: italic;
        }}
        
        /* Líneas horizontales */
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 40px 0;
        }}
        
        /* Énfasis */
        strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        
        em {{
            color: #555;
        }}
        
        /* Enlaces */
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        /* Emojis y símbolos */
        .emoji {{
            font-size: 1.2em;
        }}
        
        /* Alertas especiales */
        p:has(> strong:first-child) {{
            padding: 12px;
            border-radius: 4px;
            margin: 15px 0;
        }}
        
        /* Portada */
        .cover {{
            text-align: center;
            padding: 100px 0;
        }}
        
        .cover h1 {{
            font-size: 48pt;
            margin-bottom: 20px;
        }}
        
        .cover p {{
            font-size: 14pt;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_body}
    </div>
    
    <script>
        // Mejorar la presentación de tablas
        document.addEventListener('DOMContentLoaded', function() {{
            // Agregar clase a tablas para mejor estilo
            const tables = document.querySelectorAll('table');
            tables.forEach(table => {{
                table.style.fontSize = '10pt';
            }});
        }});
    </script>
</body>
</html>"""
    
    # Guardar HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"✅ HTML generado exitosamente: {html_file}")
    print(f"📄 Tamaño del archivo: {Path(html_file).stat().st_size / 1024:.2f} KB")
    print("\n📋 Para convertir a PDF:")
    print("   1. Abra el archivo HTML en su navegador")
    print("   2. Presione Ctrl+P (Imprimir)")
    print("   3. Seleccione 'Guardar como PDF' como destino")
    print("   4. Ajuste los márgenes si es necesario")
    print("   5. Haga clic en 'Guardar'")

if __name__ == "__main__":
    # Rutas de archivos
    md_file = Path(__file__).parent / "MANUAL_USUARIO_ES.md"
    html_file = Path(__file__).parent / "MANUAL_USUARIO_ES.html"
    
    # Verificar que el archivo Markdown existe
    if not md_file.exists():
        print(f"❌ Error: No se encuentra el archivo {md_file}")
        exit(1)
    
    # Convertir
    try:
        convert_markdown_to_html(md_file, html_file)
        print("\n🎉 Conversión completada con éxito!")
        print(f"\n🌐 Abra el archivo en su navegador: {html_file.absolute()}")
    except Exception as e:
        print(f"❌ Error durante la conversión: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
