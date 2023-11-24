# AlgoliaTypesenseCrawler
Este proyecto esta realizado para la busqueda de informacion que coincida en la pagina.

El crawler viene ya con algunos regex para poder conseguir las keys de algolia y typesense segun viene en su documentacion.

## Algolia
para la API de algolia se realiza de la siguiente forma la conexion con javascript:
``` javascript
import algoliasearch from 'algoliasearch/lite';

 const searchClient = algoliasearch(
    'ApplicationID', 
    'SearchOnlyAPIKey');
```
Donde el application ID, es de 32 caracteres y el search only de 10 caracteres. por esto mismo para hacer la busqueda para aplicaciones que usen algolia se usa lo siguiente:

``` 
"pre-Algolia": (\w*algolia\w*?):"(.+?)"
"Algolia" : "(\w{10}|\w{32})"\s*,\s*"(\w{10}|\w{32})"

```

con esto se puede hacer la busqueda de los funciones que puedan contener el formato de una busqueda de algolia, o que guardaran la key con el nombre de algolia para conseguirlas.

## Typesense
Con typesense es algo similar puesto que la sintaxis para realizar la busqueda en typesense es la siguiente:

``` jsx
const Typesense = require('typesense')

let client = new Typesense.SearchClient({
  'nodes': [{
    'host': '<URL>', 
    'port': '<PORT>',     
    'protocol': '<PROTOCOL>'   
  }],
  'apiKey': '<API_KEY>',
  'connectionTimeoutSeconds': 2
})

```

por lo cual lo vuelve mas complicado de buscar pero se puede intentar encontrar, por la alguna key que se este guardando en alguna variable (de logitud entre 32 y 200 caracteres), o por poner directamente toda la configuracion.

por lo gual se puede intentar conseguir el acceso al buscador de typesense con las siguientes expresiones regulares.

```
    "api-key" : "[a-zA-Z0-9]{32,200}\s*"'
    "Typesense" : SearchClient\([a-zA-Z0-9\(\)\[\]\{\}\.\'",:\-]*\)
```

Con esto en ejecuciones se puede conseguir las claves de algunos sitios que esten utilizando algolia o typesense de forma automatica.

## Redireccionamiento
para el redireccionamiento del crawler y que no se quede escaneando todo internet hacemos uso de mas expresiones regulares!!!

simplemente ya tengo agregado en el codigo dos principalmente para probar.

``` py
URL_REGEX =  [
                START_URL + r"\/.*" 
                r"^https?:\/\/[a-zA-Z0-9.-]+\/.*" 
            ]
```

el primer regex es para simplemente conseguir cualquier pagina web que sea una redireccion de la pagina web inicial.

y el segundo regex es usando para entrar a cualquier sitio web pero solo accediendo desde el inicio del dominio.

con esto se puede intentar realizar la busqueda y dependiendo cual sea el limite o cuales son las paginas las cuales se estan dispuestas a investigar, simplemente se debe de agregar la expresion regular para determinar a exactamente cual tiene permitido redireccionarse.

## Uso del proyecto

Este proyecto principalmente esta hecho para ayudar a investigadores a tener acceso a bases de datos que estan en algolia o typesense de forma mas facil. aunque este no puede ser su unico uso, puesto que realmente este programa puede ser para investigar cualquier pagina web e intentar buscar algun texto en especifico que contenga, ya sea el propio sitio web o cualquiera de sus javascript.