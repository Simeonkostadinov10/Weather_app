import os
from tkinter import messagebox
import customtkinter as ctk
from dotenv import load_dotenv
import requests

# Зарежда променливите от .env файла
load_dotenv()


API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def fetch_weather_data(city):
    """Извлича данните за времето от OpenWeatherMap API."""
    params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "bg"}
    try:
        response = requests.get(BASE_URL, params=params, timeout=5)
        data = response.json()
        return data
    except requests.exceptions.RequestException:
        return None

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
class Weather_app(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Weather App")
        self.geometry("450x500")
        self.resizable(width=True, height=True)

        self.title_label = ctk.CTkLabel(self,
            text="Прогноза за времето",font=("Arial", 22, "bold"),text_color="white",)
        self.title_label.pack(pady=(20, 10))

        # Поле за въвеждане на град
        self.city_entry = ctk.CTkEntry(self,placeholder_text="Въведи град (напр. Sofia, Varna)",width=300,height=40,)
        self.city_entry.pack(pady=10)

        #Бутон за търсене
        self.search_button = ctk.CTkButton(self,text="Провери",
            command=self.show_weather,width=300,height=40,fg_color="#333333",hover_color="#555555",text_color="white",)
        self.search_button.pack(pady=5)

        # Свързване на Enter клавиша
        self.bind("<Return>", lambda event: self.show_weather())

        self.result_frame = ctk.CTkFrame(self,width=320,height=260,fg_color="#1a1a1a")
        self.result_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Етикети вътре в резултатите
        self.city_label = ctk.CTkLabel(self.result_frame,text="--",font=("Arial", 20, "bold"),text_color="white",)
        self.city_label.pack(pady=(15, 5))

        self.temp_label = ctk.CTkLabel(self.result_frame,text="--°C",font=("Arial", 36, "bold"),text_color="white",)
        self.temp_label.pack(pady=5)

        self.desc_label = ctk.CTkLabel(self.result_frame,text="--",font=("Arial", 16, "italic"),text_color="#cccccc",)
        self.desc_label.pack(pady=5)

        self.details_label = ctk.CTkLabel(self.result_frame,text="Влажност: --% | Усеща се: --°C",font=("Arial", 13),text_color="#aaaaaa",)
        self.details_label.pack(pady=(10, 15))

    def show_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showerror("Грешка", "Моля, въведи име на град!")
            return

        data = fetch_weather_data(city)
        if data is None:
            messagebox.showerror("Грешка", "Проблем с интернет връзката към сървъра!")
            return

        cod = str(data.get("cod"))
        if cod == "200":
            city_name = data.get("name")
            country = data["sys"].get("country", "")
            temp = round(data["main"]["temp"])
            feels_like = round(data["main"]["feels_like"])
            desc = data["weather"][0]["description"].capitalize()
            humidity = data["main"]["humidity"]

            # Обновяване на интерфейса
            self.city_label.configure(text=f"{city_name}, {country}")
            self.temp_label.configure(text=f"{temp}°C")
            self.desc_label.configure(text=desc)
            self.details_label.configure(
            text=f"Влажност: {humidity}% | Усеща се: {feels_like}°C")

        elif cod == "404":
            messagebox.showwarning("Няма резултат", f"Градът '{city}' не беше намерен!")
        elif cod == "401":
            messagebox.showerror("Невалиден ключ","API ключът все още не е активен. Изчакай 10-15 минути!",)
        else:
            messagebox.showerror("Грешка", data.get("message", "Възникна неочаквана грешка."))


if __name__ == "__main__":
    app = Weather_app()
    app.mainloop()

