from webplex.router import HTTPRouter

def index(request, response):
    response.write("welcome!\n")

def hello(request, response):
    name = request.urlvars.get('name')
    response.write('Hello {}'.format(name))

router = HTTPRouter()
router.get('/', index)
router.get('/hello/{name}', hello)

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    host, port = "0.0.0.0", 8080
    httpd = make_server(host, port, router)
    print("Serving on port {}".format(port))
    httpd.serve_forever()


