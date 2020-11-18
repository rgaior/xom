#from app import create_app

#server = create_app()


"""Application entry point."""
from app import create_app


#def main():
server = create_app()
#   app.run(host='0.0.0.0', debug=True)


if __name__ == "__main__":
#   app = create_app()
   server.run(host='0.0.0.0', debug=True)
#   app.run(host='0.0.0.0', debug=True)
#   main()
