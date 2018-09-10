import random

class Books:
    def __init__(self):
        self._books = [
         "Crime and Punishment",
         "The Brothers Karamazov",   
         "Anna Karenina",   
         "The Master and Margarita",   
         "War and Peace",   
         "The Idiot",   
         "Lolita",   
         "Dead Souls",   
         "Eugene Onegin",   
         "Fathers and Sons",   
         "Doctor Zhivago",   
         "One Day in the Life of Ivan Denisovich",   
         "A Hero of Our Time",   
         "The Death of Ivan Ilych",   
         "Heart of a Dog",   
         "We",   
         "Oblomov",   
         "The Twelve Chairs",   
         "The Cherry Orchard",   
         "The Gambler",   
         "The Overcoat",   
         "The Seagull",   
         "And Quiet Flows the Don",   
        ]

    def get_random_book(self):
        return random.choice(self._books)
