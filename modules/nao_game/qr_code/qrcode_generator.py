import qrcode
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from database.question_repository import QuestionRepository

animals = QuestionRepository.get_all_answers()
animals.append("repeter")

# Dossier où les QR codes seront enregistrés
output_dir = "qrcode_images"
os.makedirs(output_dir, exist_ok=True)

for animal in animals:
    # Créer un QR code pour chaque animal
    qr = qrcode.QRCode(
        version=1,  # version 1 → 21x21 points
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(animal)
    qr.make(fit=True)

    # Générer l'image
    img = qr.make_image(fill_color="black", back_color="white")

    # Sauvegarder l'image
    filename = f"{animal}.png"
    filepath = os.path.join(output_dir, filename)
    img.save(filepath)
    print(f"QR code généré : {filepath}")

print("Tous les QR codes ont été générés")
