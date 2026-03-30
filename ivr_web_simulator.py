from flask import Flask, request, render_template_string

app = Flask(__name__)

menus = {
    "main": {
        "title": "IRCTC IVR SYSTEM",
        "options": {
            "1": ("Train Search", "train"),
            "2": ("PNR Status", "pnr"),
            "3": ("Ticket Booking", "booking"),
            "4": ("Cancel Ticket", "cancel"),
            "9": ("Customer Support", "support"),
            "0": ("Exit", "exit")
        }
    },

    "train": {
        "title": "Train Search",
        "options": {
            "1": ("Hyderabad → Delhi", "result1"),
            "2": ("Hyderabad → Chennai", "result2"),
            "3": ("Hyderabad → Mumbai", "result3"),
            "0": ("Main Menu", "main")
        }
    },

    "pnr": {
        "title": "PNR Status",
        "options": {
            "1": ("Check Sample PNR", "pnr_result"),
            "0": ("Main Menu", "main")
        }
    },

    "booking": {
        "title": "Ticket Booking",
        "options": {
            "1": ("Sleeper Class", "book1"),
            "2": ("AC Class", "book2"),
            "0": ("Main Menu", "main")
        }
    },

    "cancel": {
        "title": "Cancel Ticket",
        "options": {
            "1": ("Cancel Ticket", "cancel_result"),
            "0": ("Main Menu", "main")
        }
    },

    "support": {
        "title": "Customer Support",
        "options": {
            "1": ("Talk to Agent", "support_result"),
            "0": ("Main Menu", "main")
        }
    }
}

results = {
    "result1": "Train 12723 Telangana Express Available",
    "result2": "Train 12604 Chennai Express Available",
    "result3": "Train 11014 Mumbai Express Available",
    "pnr_result": "PNR Confirmed | Coach S3 | Seat 45",
    "book1": "Sleeper Ticket Booked Successfully",
    "book2": "AC Ticket Booked Successfully",
    "cancel_result": "Ticket Cancelled Successfully",
    "support_result": "Connecting to Customer Support",
    "exit": "Thank you for using IRCTC"
}

current_menu = "main"

html = """
<h1>{{title}}</h1>

{% if result %}
<h2>{{result}}</h2>
<a href="/">Restart</a>
{% else %}

<form method="post">
{% for key,value in options.items() %}
<button name="choice" value="{{key}}">
{{key}} : {{value[0]}}
</button><br><br>
{% endfor %}
</form>

{% endif %}
"""

@app.route("/", methods=["GET","POST"])
def ivr():

    global current_menu

    if request.method == "POST":

        choice = request.form["choice"]

        if choice in menus[current_menu]["options"]:

            next_state = menus[current_menu]["options"][choice][1]

            if next_state in results:
                result = results[next_state]
                current_menu = "main"
                return render_template_string(html,title="Result",result=result)

            else:
                current_menu = next_state

    menu = menus[current_menu]

    return render_template_string(html,title=menu["title"],options=menu["options"],result=None)


if __name__ == "__main__":
    app.run(debug=True) 