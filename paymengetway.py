import qrcode
from flask import Flask, request, jsonify

app = Flask(__name__)

# Function to generate UPI link
def generate_upi_link(upi_id, name, amount, note):
    """
    Generates a UPI payment link.
    Args:
        upi_id (str): UPI ID (e.g., example@upi)
        name (str): Payee name
        amount (float): Amount to be paid
        note (str): Payment note
    Returns:
        str: UPI payment link
    """
    return f"upi://pay?pa={upi_id}&pn={name}&am={amount}&cu=INR&tn={note}"

# Function to generate QR code
def generate_upi_qr(upi_link, filename="upi_qr.png"):
    """
    Generates a QR code for the UPI link.
    Args:
        upi_link (str): The UPI payment link
        filename (str): File name to save the QR code image
    """
    qr = qrcode.QRCode()
    qr.add_data(upi_link)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    img.save(filename)
    return filename

# API route to create payment link and QR code
@app.route("/create-payment", methods=["POST"])
def create_payment():
    """
    API to create a UPI payment link and corresponding QR code.
    Input JSON:
        - upi_id: UPI ID (e.g., example@upi)
        - name: Payee name
        - amount: Payment amount
        - note: Payment note
    Output:
        - UPI link
        - QR code image path
    """
    try:
        # Get data from request
        data = request.json
        upi_id = data["upi_id"]
        name = data["name"]
        amount = data["amount"]
        note = data["note"]

        # Generate UPI link
        upi_link = generate_upi_link(upi_id, name, amount, note)

        # Generate QR code
        qr_filename = f"{upi_id}_upi_qr.png"
        qr_path = generate_upi_qr(upi_link, qr_filename)

        # Return response
        return jsonify({
            "upi_link": upi_link,
            "qr_code_path": qr_path
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(port=5000)
