#!/bin/bash

# Exporta as variáveis do .env (somente se estiver no ambiente local)
export $(grep -v '^#' .env | xargs)

# Inicia o servidor Flask com Gunicorn
gunicorn -w 4 -b 0.0.0.0:$PORT arena:app
