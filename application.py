from flask import Flask

application = Flask(__name__)


@application.route('/')
def main():
    return "핵심 쏙쏙 AWS"

if __name__ == '__main__':
    application.debug = True
    application.run()