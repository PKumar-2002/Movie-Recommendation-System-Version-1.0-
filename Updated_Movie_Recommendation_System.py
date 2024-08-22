from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image, AsyncImage
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget  # Import Widget
import requests
import pandas as pd
import random

class ImageButton(ButtonBehavior, Image):
    pass

class FilmFavorApp(App):
    def build(self):
        Window.size = (800, 526)
        Window.title = 'Film Favor'
        Window.borderless = True

        layout = FloatLayout()

        background_image = Image(source='Background.png', allow_stretch=True, keep_ratio=False, size=Window.size)
        background_image.pos = (0, 0)
        layout.add_widget(background_image)

        close_btn = Button(
            text="Close",
            size_hint=(None, None),
            size=(60, 44),
            pos_hint={'center_x': 0.9, 'center_y': 0.1},
            font_name='chesnagrotesk-medium.otf',
            halign='center',
            background_color=(1, 1, 1, 0.2)
        )
        close_btn.bind(on_press=self.close_window)
        layout.add_widget(close_btn)

        title_label = Label(
            text="Film Favor",
            font_name='chesnagrotesk-medium.otf',
            font_size=30,
            bold=True,
            color=(0, 0, 0, 1),
            size_hint=(None, None),
            size=(300, 50)
        )
        title_label.pos_hint = {"center_x": 0.52, "y": 0.91}
        layout.add_widget(title_label)

        surprise_label = Label(
            text="Surprise Me :)",
            font_name='chesnagrotesk-medium.otf',
            font_size=20,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(20, 20)
        )
        surprise_label.pos_hint = {"center_x": 0.19, "y": 0.56}
        layout.add_widget(surprise_label)

        icon_image = Image(source='video-camera.png', size_hint=(None, None), size=(50, 50))
        icon_image.pos_hint = {"x": 0.39, "y": 0.91}
        layout.add_widget(icon_image)

        movies = pd.read_csv('tmdb_5000_movies.csv')
        credits = pd.read_csv('tmdb_5000_credits.csv')
        movies = movies.merge(credits, on='title')

        def preprocess_data():
            movies['genres'] = movies['genres'].apply(lambda x: [genre['name'] for genre in eval(x)])
            return movies

        movies = preprocess_data()

        unique_genres = sorted(set(genre for sublist in movies['genres'] for genre in sublist))

        genre_spinner = Spinner(
            text='Select Genre',
            values=unique_genres,
            size_hint=(None, None),
            size=(130, 44),
            pos_hint={'center_x': 0.18, 'center_y': 0.85},
            background_normal='',
            background_color=(1, 1, 1, 0.3),
            color=(0, 0, 0, 1),
            font_size=18,
            font_name='chesnagrotesk-medium.otf'
        )
        layout.add_widget(genre_spinner)

        recommendation_input = TextInput(
            text='5',
            multiline=False,
            size_hint=(None, None),
            size=(130, 44),
            pos_hint={'center_x': 0.18, 'center_y': 0.77},
            font_size=18,
            font_name='chesnagrotesk-medium.otf',
            halign='center',
            background_color=(1, 1, 1, 0.3)
        )
        layout.add_widget(recommendation_input)

        search_input = TextInput(
            hint_text='Search for a movie',
            multiline=False,
            size_hint=(None, None),
            size=(300, 44),
            pos_hint={'center_x': 0.49, 'center_y': 0.85},
            font_size=18,
            font_name='chesnagrotesk-medium.otf',
            halign='center',
            background_color=(1, 1, 1, 0.5)
        )
        layout.add_widget(search_input)

        result_box = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=200,
            pos_hint={'center_x': 0.44, 'center_y': 0.27},
            spacing=10,  # Adjust spacing as needed
            padding=[10, 0, 10, 0]  # Add padding to the left and right sides
        )
        layout.add_widget(result_box)

        def fetch_poster(title):
            api_key = 'OMDB'  # Replace with your OMDb API key
            url = f'http://www.omdbapi.com/?t={title}&apikey={api_key}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'Poster' in data and data['Poster'] != 'N/A':
                    return AsyncImage(source=data['Poster'], size_hint=(None, None), size=(100, 150))
            return Label(text="No Image", size_hint=(None, None), size=(100, 150))

        def search_movie(instance):
            result_box.clear_widgets()
            search_query = search_input.text.lower()
            if search_query.strip():
                matching_movies = movies[movies['title'].str.lower().str.contains(search_query)]
                matching_movies = matching_movies.head(5)
                if not matching_movies.empty:
                    for index, row in matching_movies.iterrows():
                        movie_poster = fetch_poster(row['title'])

                        spacer_vertical = Widget(size_hint_y=None, height=10)  # Vertical spacer

                        movie_title = Label(
                            text=row['title'],
                            font_name='chesnagrotesk-medium.otf',
                            font_size=16,
                            size_hint_y=None,
                            height=100,
                            halign='center',
                            valign='middle'
                        )
                        movie_title.bind(size=movie_title.setter('text_size'))

                        movie_layout = BoxLayout(orientation='vertical', size_hint=(None, 1), size=(120, 210))  # Adjusted width for the spacer
                        movie_layout.add_widget(movie_poster)
                        movie_layout.add_widget(spacer_vertical)  # Add the vertical spacer between poster and title
                        movie_layout.add_widget(movie_title)

                        spacer_horizontal = Widget(size_hint_x=None, width=20)  # Horizontal spacer

                        result_box.add_widget(spacer_horizontal)  # Add the horizontal spacer between movie items
                        result_box.add_widget(movie_layout)
                    
                    # Center align all movies with equal padding on both sides
                    empty_space = (Window.width - (len(matching_movies) * 120 + (len(matching_movies) - 1) * 20)) / 2
                    result_box.padding = [empty_space, 0, empty_space, 0]
                else:
                    result_box.add_widget(Label(text="No matching movies found.", size_hint=(1, None), halign='center'))
            else:
                result_box.add_widget(Label(text="Please enter a valid search query.", size_hint=(1, None), halign='center'))

        def get_recommendations(genre, num_recommendations):
            filtered_movies = movies[movies['genres'].apply(lambda x: genre in x)]
            shuffled_movies = filtered_movies.sample(frac=1, random_state=random.randint(1, 10000))
            return shuffled_movies.head(int(num_recommendations))

        def recommend(instance):
            result_box.clear_widgets()
            selected_genre = genre_spinner.text
            num_recommendations = recommendation_input.text
            if selected_genre != 'Select Genre' and num_recommendations.isdigit():
                recommendations = get_recommendations(selected_genre, num_recommendations)
                for index, row in recommendations.iterrows():
                    movie_poster = fetch_poster(row['title'])

                    spacer_vertical = Widget(size_hint_y=None, height=10)  # Vertical spacer

                    movie_title = Label(
                        text=row['title'],
                        font_name='chesnagrotesk-medium.otf',
                        font_size=16,
                        size_hint_y=None,
                        height=100,
                        halign='center',
                        valign='middle'
                    )
                    movie_title.bind(size=movie_title.setter('text_size'))

                    movie_layout = BoxLayout(orientation='vertical', size_hint=(None, 1), size=(120, 210))  # Adjusted width for the spacer
                    movie_layout.add_widget(movie_poster)
                    movie_layout.add_widget(spacer_vertical)  # Add the vertical spacer between poster and title
                    movie_layout.add_widget(movie_title)

                    spacer_horizontal = Widget(size_hint_x=None, width=20)  # Horizontal spacer

                    result_box.add_widget(spacer_horizontal)  # Add the horizontal spacer between movie items
                    result_box.add_widget(movie_layout)
                
                # Center align all movies with equal padding on both sides
                empty_space = (Window.width - (len(recommendations) * 120 + (len(recommendations) - 1) * 20)) / 2
                result_box.padding = [empty_space, 0, empty_space, 0]
            else:
                result_box.add_widget(Label(text="Please select a valid genre and enter a number.", size_hint=(1, None), halign='center'))

        recommend_button = ImageButton(
            source='video-cam.png',
            size_hint=(None, None),
            size=(80, 80),
            pos_hint={'center_x': 0.19, 'center_y': 0.65},
        )
        recommend_button.bind(on_press=recommend)
        layout.add_widget(recommend_button)

        search_button = Button(
            text="Search",
            size_hint=(None, None),
            size=(130, 44),
            pos_hint={'center_x': 0.49, 'center_y': 0.77},
            font_name='chesnagrotesk-medium.otf',
            halign='center',
            background_color=(1, 1, 1, 0.3)
        )
        search_button.bind(on_press=search_movie)
        layout.add_widget(search_button)

        return layout
    
    def close_window(self, instance):
        App.get_running_app().stop()

if __name__ == '__main__':
    FilmFavorApp().run()
