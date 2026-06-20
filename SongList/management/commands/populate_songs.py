from django.core.management.base import BaseCommand
from SongList.models import Musica
import requests

class Command(BaseCommand):
    help = 'Comando para popular o banco de dados com músicas da iTunes Search API'

    def handle(self, *args, **options):
        # Lista de artistas/bandas populares para buscar
        artistas = [
            'Beatles', 'Queen', 'Charli XCX', 'Linkin Park', "Magdalena Bay",
            'Beyoncé', 'Britney Spears', 'Sade', 'Tears For Fears',
            'Sabrina Carpenter', 'Olivia Rodrigo', 'Madonna', 'Michael Jackson',
            'Elvis Presley', 'Fleetwood Mac', 'Bruno Mars', "Clairo", 'Dua Lipa',
            'Hayley Williams', 'Paramore', 'Billie Eilish', 'Phoebe Bridgers',
            "underscores", "Ninajirachi", 'Rina Sawayama', 'Mitski', 'FKA Twigs', 
            'Arctic Monkeys', 'The Strokes', "Slayyter", "Oklou", "Sky Ferreira",
            "PinkPantheress", "Grimes", "Phil Collins", "Marina Sena",
            "Chappel Roan", "Caroline Polachek", "Hozier", "Addison Rae",
            "Doja Cat", "Lady Gaga", "Gorillaz", "The Marías",
        ]

        total_adicionadas = 0

        for artista in artistas:
            try:
                # Requisição para iTunes Search API
                url = 'https://itunes.apple.com/search'
                params = {
                    'term': artista,
                    'media': 'music',
                    'entity': 'song',
                    'limit': 10
                }

                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                dados = response.json()

                # Processa os resultados
                for item in dados.get('results', []):
                    # Verifica se a música já existe
                    titulo = item.get('trackName', '')
                    artista_item = item.get('artistName', '')

                    if titulo and artista_item:
                        musica_existente = Musica.objects.filter(
                            titulo=titulo,
                            artista=artista_item
                        ).exists()

                        if not musica_existente:
                            musica = Musica.objects.create(
                                titulo=titulo,
                                artista=artista_item,
                                album=item.get('collectionName', ''),
                                ano=int(item.get('releaseDate', '0000')[:4])
                            )
                            total_adicionadas += 1

                self.stdout.write(
                    self.style.SUCCESS(f'Escrito com sucesso: {artista}')
                )

            except requests.exceptions.RequestException as e:
                self.stdout.write(
                    self.style.WARNING(f'Erro! ao buscar {artista}: {str(e)}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro! processando {artista}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nConcluído! {total_adicionadas} músicas adicionadas!'
            )
        )
