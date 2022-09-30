import pandas as pd
import re
import html2text

df = pd.read_json("../metadata/meta_electronics_17_18.json")

h = html2text.HTML2Text()


def txt2spec(df, i):
    t = h.handle((df["tech1"][i]))
    t = t[:-2] + "  " + "\n"
    labels = re.findall(r"[^|\n*+]+  |  +[^|\n*+]", t[52:], re.I)
    labels = [x.strip() for x in labels]
    return labels


prev = [
    '6mm (1/2" 3/8" 1/4")',
    "1600",
    "768 pixels",
    "A- US style",
    "Protection, 4. Fast Power Battery        Charger",
    "Wall \
Power Cord, 1 X Car Power Cord, 1 X User Manual",
    "14430 14250 10440" "MHz",
    "10 A",
    "800",
    "310 lm",
    "millimeters",
    "1.49 Inch\
",
    "1.49 Inches",
    "5 Refills" "FCAM1",
    "40W, each up to 2.4A",
    "2x5TB",
    "YCAM1",
    '\
6mm (1/2" 3/8" 1/4")',
    "6.6ft - 2 Pack" "CAT7-6FT-BK",
    "Keeper",
    "2USB",
    '17" LCD',
    "Smooth",
    "600",
]

post = ["(", "D", "F", "Optional", "Flat"]

df["specs"] = ""

for i in range(len(df)):
    df.loc[i, "specs"] = txt2spec(df, i)

letters = []
up_letters = []

for one in range(97, 123):
    letters.append(chr(one))

for let in letters:
    up_letters.append(let.upper())

for i in range(len(df)):

    for j in letters:
        if j in df.loc[i, "specs"]:
            if j == "i":
                if j in df.loc[i, "specs"]:
                    ind = df.loc[i, "specs"].index(j)
                    if df.loc[i, "specs"][ind + 1] == "Item model number":
                        continue
            ind = df.loc[i, "specs"].index(j)
            df.loc[i, "specs"][ind] = df.loc[i, "specs"][ind] + " "
            +df.loc[i, "specs"][ind + 1]
            df.loc[i, "specs"].pop(ind + 1)

    for j in up_letters:
        try:
            if j == "P":
                if j in df.loc[i, "specs"]:
                    ind = df.loc[i, "specs"].index(j)
                    if df.loc[i, "specs"][ind + 1] == "Item model number":
                        continue
                    if df.loc[i, "specs"][ind + 1] == "517-PWR55-36998":
                        continue
                    elif (
                        (
                            df.loc[i, "specs"][ind + 1]
                            == "Store\
"
                        )
                        or (df.loc[i, "specs"][ind + 1] == "TAG05020-AA5")
                    ):
                        df.loc[i, "specs"][ind] = df.loc[i, "specs"][ind] + " "
                        +df.loc[i, "specs"][ind + 1]
                        df.loc[i, "specs"].pop(ind + 1)

            if j == "N":
                if j in df.loc[i, "specs"]:
                    ind = df.loc[i, "specs"].index(j)

                    if (
                        (
                            df.loc[i, "specs"][ind + 1]
                            == "1\
                    "
                        )
                        or (df.loc[i, "specs"][ind + 1] == "2")
                        or (
                            df.loc[
                                i,
                                "specs\
                    ",
                            ][ind + 1]
                            == "3"
                        )
                        or (df.loc[i, "specs"][ind + 1] == "4")
                    ):

                        continue

                    elif (
                        (
                            df.loc[i, "specs"][ind + 1]
                            == "Store\
                    "
                        )
                        or (df.loc[i, "specs"][ind + 1] == "TAG05020-AA5")
                    ):
                        df.loc[i, "specs"][ind] = (
                            df.loc[i, "specs"][ind]
                            + " \
                        "
                            + df.loc[i, "specs"][ind + 1]
                        )
                        df.loc[i, "specs"].pop(ind + 1)

            if j == "B":
                if j in df.loc[i, "specs"]:
                    ind = df.loc[i, "specs"].index(j)
                    if df.loc[i, "specs"][ind + 1] == "Size":
                        continue
            if j in df.loc[i, "specs"]:
                ind = df.loc[i, "specs"].index(j)
                df.loc[i, "specs"][ind] = (
                    df.loc[i, "specs"][ind] + " " + df.loc[i, "specs"][ind + 1]
                )
                df.loc[i, "specs"].pop(ind + 1)

        except KeyError:
            pass

    if "Processor" in df.loc[i, "specs"]:
        try:
            ind = df.loc[i, "specs"].index("Processor")
            if len(df.loc[i, "specs"][ind + 1]) == 1:
                df.loc[i, "specs"][ind + 1] = (
                    df.loc[i, "specs"][ind + 1]
                    + " "
                    + df.loc[
                        i,
                        "\
                    specs",
                    ][ind + 2]
                )
                df.loc[i, "specs"].pop(ind + 1)
        except KeyError:
            pass

    if "ounces" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("ounces")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)

    try:
        if "3" in df.loc[i, "specs"]:
            ind = df.loc[i, "specs"].index("3")
            if not (
                (df.loc[i, "specs"][ind - 1] == "Number of USB 2.0 Ports")
                or (df.loc[i, "specs"][ind - 1] == "Number of USB 3.0 Ports")
                or (df.loc[i, "specs"][ind - 1] == "Hard Drives")
            ):
                df.loc[i, "specs"][ind] = (
                    df.loc[i, "specs"][ind] + " " + df.loc[i, "specs"][ind + 1]
                )
                df.loc[i, "specs"].pop(ind + 1)
    except KeyError:
        pass

    try:
        if "1" in df.loc[i, "specs"]:
            ind = df.loc[i, "specs"].index("1")
            if df.loc[i, "specs"][ind + 1] == "Radio":
                df.loc[i, "specs"][ind] = (
                    df.loc[i, "specs"][ind] + " " + df.loc[i, "specs"][ind + 1]
                )
                df.loc[i, "specs"].pop(ind + 1)

            if df.loc[i, "specs"][ind - 1] == "Max Screen Resolution":
                df.loc[i, "specs"][ind] = (
                    df.loc[i, "specs"][ind] + " " + df.loc[i, "specs"][ind + 1]
                )
                df.loc[i, "specs"].pop(ind + 1)

    except KeyError:
        pass

    try:
        if "4" in df.loc[i, "specs"]:
            ind = df.loc[i, "specs"].index("4")
            if not (
                (df.loc[i, "specs"][ind - 1] == "Number of USB 2.0 Ports")
                or (df.loc[i, "specs"][ind - 1] == "Number of USB 3.0 Ports")
                or (df.loc[i, "specs"][ind - 1] == "Part Number")
            ):
                df.loc[i, "specs"][ind] = (
                    df.loc[i, "specs"][ind] + " " + df.loc[i, "specs"][ind + 1]
                )
                df.loc[i, "specs"].pop(ind + 1)
    except KeyError:
        pass

    try:
        if "8" in df.loc[i, "specs"]:
            ind = df.loc[i, "specs"].index("8")
            if not (
                (df.loc[i, "specs"][ind - 1] == "Number of USB 2.0 Ports")
                or (df.loc[i, "specs"][ind - 1] == "Number of Items")
            ):
                df.loc[i, "specs"][ind] = (
                    df.loc[i, "specs"][ind] + df.loc[i, "specs"][ind + 1]
                )
                df.loc[i, "specs"].pop(ind + 1)
    except KeyError:
        pass

    if "inches" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("inches")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)
    if "Leopard" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("Leopard")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)
    if "EXT-CON-75FT-100FT" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("EXT-CON-75FT-100FT")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)
    if "for Proposition 65 warning" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("for Proposition 65 warning")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)
    if "Lite" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("Lite")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)
    if "PowerPC G4" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("PowerPC G4")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)
    if "Brands" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("Brands")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)
    if "Frama Classic Magnetic" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("Frama Classic Magnetic")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)
    if "Cables To Go" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("Cables To Go")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)
    if "Frama Horizontal Pouch" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("Frama Horizontal Pouch")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)
    if "centimeters" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("centimeters")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)
    if "ELECTRONICS" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("ELECTRONICS")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)
    if "Electronics" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("Electronics")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)
    if "FG-BC47" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("FG-BC47")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)

    if "pounds" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("pounds")
        if len(df.loc[i, "specs"][ind - 1]) == 1:
            df.loc[i, "specs"][ind - 1] = (
                df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
            )
            df.loc[i, "specs"].pop(ind)
    if "CPL5-BG" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("CPL5-BG")
        df.loc[i, "specs"][ind - 1] = (
            df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
        )
        df.loc[i, "specs"].pop(ind)
    if "Power" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("Power")
        if df.loc[i, "specs"][ind - 1] == "B":
            df.loc[i, "specs"][ind - 1] = (
                df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
            )
            df.loc[i, "specs"].pop(ind)
    for j in prev:
        try:
            if j in df.loc[i, "specs"]:
                ind = df.loc[i, "specs"].index(j)
                df.loc[i, "specs"][ind - 1] = (
                    df.loc[i, "specs"][ind - 1] + " " + df.loc[i, "specs"][ind]
                )
                df.loc[i, "specs"].pop(ind)
        except KeyError:
            pass
    for j in post:
        try:
            if j in df.loc[i, "specs"]:
                ind = df.loc[i, "specs"].index(j)
                df.loc[i, "specs"][ind] = (
                    df.loc[i, "specs"][ind] + " " + df.loc[i, "specs"][ind + 1]
                )
                df.loc[i, "specs"].pop(ind + 1)
        except KeyError:
            pass

df["spec_dict"] = ""
lst_dict = []
for j in range(len(df)):
    ks = []
    vs = []
    for i in range(len(df.loc[j, "specs"])):
        if i % 2 == 0:
            ks.append(df.loc[j, "specs"][i])
        if i % 2 != 0:
            vs.append(df.loc[j, "specs"][i])
    lst_dict.append(dict(zip(ks, vs)))

print(lst_dict)
df["spec_dict"] = lst_dict

df.to_json("Meta_v1.json")
