import pandas as pd
import html2text
import re
import pickle

df = pd.read_json("Meta_v2.json")

with open("del_list.txt", "rb") as fp:  # Unpickling products to be deleted
    del_list = pickle.load(fp)

for i in range(len(df)):
    if df.loc[i, "spec_dict"] in del_list:
        df = df.drop(i, axis=0)

df = df.reset_index()
df = df.drop("index", axis=1)

prev = [
    "MHz",
    "6.6ft - 2 Pack",
    "900 pixels",
    "5 Refills",
    "FCAM1",
    "800 pixels",
    "1200 pixels",
    "GHz Radio Frequency, 802.11abg",
    '6mm (1/2" 3/8" 1/4")',
]
sep = ["3 Size", "P Model", "8Batteries Included?", "4 Size"]

for i in range(len(df)):

    for j in prev:
        if j in df.loc[i, "specs"]:
            if j == "800 pixels":
                ind = df.loc[i, "specs"].index(j)
                if not (df.loc[i, "specs"][ind - 1] == "1"):
                    continue
            if j == "1200 pixels":
                ind = df.loc[i, "specs"].index(j)
                if df.loc[i, "specs"][ind - 1] == "1":
                    df.loc[i, "specs"][ind - 1] = "1920x1200 pixels"
                    df.loc[i, "specs"].pop(ind)
                    break
                break
            ind = df.loc[i, "specs"].index(j)
            df.loc[i, "specs"][ind - 1] = (
                df.loc[
                    i,
                    "specs            \
                ",
                ][ind - 1]
                + df.loc[i, "specs"][ind]
            )
            df.loc[i, "specs"].pop(ind)

    for j in sep:
        if j in df.loc[i, "specs"]:
            ind = df.loc[i, "specs"].index(j)
            rep = (
                df.loc[i, "specs"][ind][
                    1:len(
                        df.loc[
                            i,
                            "specs\
            ",
                        ][ind]
                    )
                ]
            ).strip()
            df.loc[i, "specs"][ind] = df.loc[i, "specs"][ind][0]
            df.loc[i, "specs"].insert(ind + 1, rep)

    if "Processor PowerPC G4" in df.loc[i, "specs"]:
        ind = df.loc[i, "specs"].index("Processor PowerPC G4")
        df.loc[i, "specs"][ind] = "Processor"
        df.loc[i, "specs"].insert(ind + 1, "PowerPC G4")

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

# print(lst_dict)
df["spec_dict"] = lst_dict


# In[228]:


h = html2text.HTML2Text()
df["specs2"] = ""


def txt2spec(df, i):
    t = h.handle((df["tech2"][i]))
    t = t[:-2] + "  " + "\n"
    labels = re.findall(r"[^|\n*+]+  |  +[^|\n*+]", t[52:], re.I)
    labels = [x.strip() for x in labels]
    return labels


for i in range(len(df)):
    df.loc[i, "specs2"] = txt2spec(df, i)

merge = [
    "A",
    "[",
    "C",
    "U",
    "F",
    "D",
    "G",
    "H",
    "J",
    "K",
    "L",
    "M",
    "P",
    "Q",
    "S",
    "T",
    "V",
    "W",
]

for i in range(len(df)):
    for j in merge:
        if j in df.loc[i, "specs2"]:
            ind = df.loc[i, "specs2"].index(j)
            if (j == "U") and (
                not (
                    df.loc[i, "specs2"][ind + 1]
                    == "\
            Networks"
                )
            ):
                continue
            if (j == "A") and (
                not (
                    df.loc[i, "specs2"][ind - 1]
                    == "Brand \
            Name"
                )
            ):
                continue
            if (j == "F") and (
                (df.loc[i, "specs2"][ind + 1] == "Drive requires reformatting")
            ):
                df.loc[i, "specs2"].pop(ind + 1)
            if (j == "F") and (not (df.loc[i, "specs2"][ind + 1] == "Design")):
                continue
            if (j == "P") and (
                not (
                    df.loc[i, "specs2"][ind + 1]
                    == "ANTENNAS, \
            INC."
                )
            ):
                continue
            if (j == "D") and (
                df.loc[i, "specs2"][ind + 1]
                == "\
            Item model number"
            ):
                continue
            if (
                (j == "D")
                and (df.loc[i, "specs2"][ind - 1] == "Series")
                and (
                    not (
                        df.loc[i, "specs2            "][ind + 1]
                        == "Item model\
                        number"
                    )
                )
            ):
                df.loc[i, "specs2"].pop(ind + 1)
            if (j == "Q") and ((df.loc[i, "specs2"][ind - 1] == "Color")):
                df.loc[i, "specs2"][ind - 1] = "Graphics Coprocessor"
                df.loc[i, "specs2"].pop(ind)
            df.loc[i, "specs2"][ind] = (
                df.loc[i, "specs2"][ind] + " " + df.loc[i, "specs2"][ind + 1]
            )
            df.loc[i, "specs2"].pop(ind + 1)

    if "US" in df.loc[i, "specs2"]:
        ind = df.loc[i, "specs2"].index("US")
        df.loc[i, "specs2"][ind - 1] = (
            df.loc[i, "specs2"][ind - 1] + " " + df.loc[i, "specs2"][ind]
        )
        df.loc[i, "specs2"].pop(ind)

    if "-US" in df.loc[i, "specs2"]:
        ind = df.loc[i, "specs2"].index("-US")
        df.loc[i, "specs2"][ind - 1] = (
            df.loc[i, "specs2"][ind - 1] + " " + df.loc[i, "specs2"][ind]
        )
        df.loc[i, "specs2"].pop(ind)

    if "versions) MAC: OS X" in df.loc[i, "specs2"]:
        ind = df.loc[i, "specs2"].index("versions) MAC: OS X")
        df.loc[i, "specs2"][ind - 1] = (
            df.loc[i, "specs2"][ind - 1] + " (" + df.loc[i, "specs2"][ind]
        )
        df.loc[i, "specs2"].pop(ind)

    if "OS X Mountain Lion or Snow Leopard" in df.loc[i, "specs2"]:
        ind = df.loc[i, "specs2"].index("OS X Mountain Lion or Snow Leopard")
        df.loc[i, "specs2"][ind - 1] = (
            df.loc[i, "specs2"][ind - 1] + " " + df.loc[i, "specs2"][ind]
        )
        df.loc[i, "specs2"].pop(ind)

    if ("W" in df.loc[i, "specs2"]) or ("w" in df.loc[i, "specs2"]):
        try:
            ind = df.loc[i, "specs2"].index("w")
        except KeyError:
            ind = df.loc[i, "specs2"].index("W")
        df.loc[i, "specs2"][ind] = (
            df.loc[i, "specs2"][ind] + " " + df.loc[i, "specs2"][ind + 1]
        )
        df.loc[i, "specs2"].pop(ind + 1)

    if "11" in df.loc[i, "specs2"]:
        ind = df.loc[i, "specs2"].index("11")
        if df.loc[i, "specs2"][ind - 1] == "6":
            df.loc[i, "specs2"][ind - 1] = (
                df.loc[i, "specs2"][ind - 1] + df.loc[i, "specs2"][ind]
            )
            df.loc[i, "specs2"].pop(ind)

    if "ounces" in df.loc[i, "specs2"]:
        ind = df.loc[i, "specs2"].index("ounces")
        df.loc[i, "specs2"][ind - 1] = (
            df.loc[i, "specs2"][ind - 1] + " " + df.loc[i, "specs2"][ind]
        )
        df.loc[i, "specs2"].pop(ind)

for i in range(len(df)):
    if "D Item model number" in df.loc[i, "specs2"]:
        ind = df.loc[i, "specs2"].index(j)
        rep = (
            df.loc[i, "specs2"][ind][
                2 : len(
                    df.loc[
                        i,
                        "\
        specs2",
                    ][ind]
                )
            ]
        ).strip()
        df.loc[i, "specs2"][ind] = df.loc[i, "specs"][ind][0]
        df.loc[i, "specs2"].insert(ind + 1, rep)
    if "GTX 1050Ti Processor Brand" in df.loc[i, "specs2"]:
        ind = df.loc[i, "specs2"].index("GTX 1050Ti Processor Brand")
        df.loc[i, "specs2"][ind] = "GTX 1050Ti"
        df.loc[i, "specs2"].insert(ind + 1, "Processor Brand")


df["spec_dict2"] = ""
lst_dict = []
for j in range(len(df)):
    ks = []
    vs = []
    for i in range(len(df.loc[j, "specs2"])):
        if i % 2 == 0:
            ks.append(df.loc[j, "specs2"][i])
        if i % 2 != 0:
            vs.append(df.loc[j, "specs2"][i])
    lst_dict.append(dict(zip(ks, vs)))

print(lst_dict)
df["spec_dict2"] = lst_dict


for i in range(len(df)):

    for v, k in enumerate(df.loc[i, "spec_dict2"]):
        replace = [
            "Package Dimensions",
            "Product Dimensions",
            "Size        ",
            "Item Dimensions",
            "Item Dimensions L x W x H",
            "Item Display dimensions L x W x H",
        ]
        if k in replace:
            df.loc[i, "spec_dict2"][
                "Item Dimensions\
            "
            ] = df.loc[i, "spec_dict2"][k]
            del df.loc[i, "spec_dict2"][k]
            break

    for v, k in enumerate(df.loc[i, "spec_dict"]):
        replace = [
            "Package Dimensions",
            "Product Dimensions",
            "        Item Dimensions",
            "Item Dimensions L x W x H",
            "Item Display dimensions L x W x H",
        ]
        if k in replace:
            df.loc[i, "spec_dict"][
                "Item Dimensions\
            "
            ] = df.loc[i, "spec_dict"][k]
            del df.loc[i, "spec_dict"][k]
            break

    for v, k in enumerate(df.loc[i, "spec_dict2"]):
        replace = ["Weight", "Item Weight"]
        if k in replace:
            df.loc[i, "spec_dict2"]["Weight"] = df.loc[i, "spec_dict2"][k]
            del df.loc[i, "spec_dict2"][k]
            break

    for v, k in enumerate(df.loc[i, "spec_dict"]):
        replace = ["Weight", "Item Weight"]
        if k in replace:
            df.loc[i, "spec_dict"]["Weight"] = df.loc[i, "spec_dict"][k]
            del df.loc[i, "spec_dict"][k]
            break

    for v, k in enumerate(df.loc[i, "spec_dict2"]):
        replace = ["Color", "Color Name"]
        if k in replace:
            df.loc[i, "spec_dict2"]["Color"] = df.loc[i, "spec_dict2"][k]
            del df.loc[i, "spec_dict2"][k]
            break

    for v, k in enumerate(df.loc[i, "spec_dict"]):
        replace = ["Color", "Color Name"]
        if k in replace:
            df.loc[i, "spec_dict"]["Color"] = df.loc[i, "spec_dict"][k]
            del df.loc[i, "spec_dict"][k]
            break

    for v, k in enumerate(df.loc[i, "spec_dict2"]):
        replace = ["Brand", "Brand Name"]
        if k in replace:
            df.loc[i, "spec_dict2"]["Brand"] = df.loc[i, "spec_dict2"][k]
            del df.loc[i, "spec_dict2"][k]
            break

    for v, k in enumerate(df.loc[i, "spec_dict"]):
        replace = ["Brand", "Brand Name"]
        if k in replace:
            df.loc[i, "spec_dict"]["Brand"] = df.loc[i, "spec_dict"][k]
            del df.loc[i, "spec_dict"][k]
            break

    for v, k in enumerate(df.loc[i, "spec_dict2"]):
        replace = [
            "Item model number",
            "Manufacturer Part Number        ",
            "Part Number",
            "National Stock Number",
            "Model",
        ]
        if k in replace:
            df.loc[i, "spec_dict2"][
                "Item model number\
            "
            ] = df.loc[i, "spec_dict2"][k]
            del df.loc[i, "spec_dict2"][k]
            break

    for v, k in enumerate(df.loc[i, "spec_dict"]):
        replace = [
            "Item model number",
            "Manufacturer Part Number        ",
            "Part Number",
            "National Stock Number",
            "Model",
        ]
        if k in replace:
            df.loc[i, "spec_dict"][
                "Item model number\
            "
            ] = df.loc[i, "spec_dict"][k]
            del df.loc[i, "spec_dict"][k]
            break

    for v, k in enumerate(df.loc[i, "spec_dict2"]):
        replace = [
            "Number of Items",
            "Item Package Quantity        ",
            "No. of Pieces",
            "No. of Componenets",
            "N",
            "No",
        ]
        if k in replace:
            df.loc[i, "spec_dict2"][
                "Item Package Quantity\
            "
            ] = df.loc[i, "spec_dict2"][k]
            del df.loc[i, "spec_dict2"][k]
            break

    for v, k in enumerate(df.loc[i, "spec_dict"]):
        replace = [
            "Number of Items",
            "Item Package Quantity        ",
            "No. of Pieces",
            "No. of Componenets",
            "N",
            "No",
        ]
        if k in replace:
            df.loc[i, "spec_dict"][
                "Item Package Quantity\
            "
            ] = df.loc[i, "spec_dict"][k]
            del df.loc[i, "spec_dict"][k]
            break

    for v, k in enumerate(df.loc[i, "spec_dict2"]):
        replace = ["Hard Drive", "Flash Memory Size"]
        if k in replace:
            df.loc[i, "spec_dict2"]["Memory Capacity"] = df.loc[
                i,
                "\
            spec_dict2",
            ][k]
            del df.loc[i, "spec_dict2"][k]
            break

    for v, k in enumerate(df.loc[i, "spec_dict"]):
        replace = ["Hard Drive", "Flash Memory Size"]
        if k in replace:
            df.loc[i, "spec_dict"][
                "Memory Capacity\
            "
            ] = df.loc[i, "spec_dict"][k]
            del df.loc[i, "spec_dict"][k]
            break

    for v, k in enumerate(df.loc[i, "spec_dict2"]):
        replace = [
            "Max Screen Resolution",
            "Screen Resolution\
        ",
            "Display Resolution",
        ]
        if k in replace:
            df.loc[i, "spec_dict2"]["Screen Resolution"] = df.loc[
                i,
                "\
            spec_dict2",
            ][k]
            del df.loc[i, "spec_dict2"][k]
            break

    for v, k in enumerate(df.loc[i, "spec_dict"]):
        replace = [
            "Max Screen Resolution",
            "Screen Resolution",
            "\
        Display Resolution",
        ]
        if k in replace:
            df.loc[i, "spec_dict"]["Screen Resolution"] = df.loc[
                i,
                "\
            spec_dict",
            ][k]
            del df.loc[i, "spec_dict"][k]
            break

UKS = []

for i in range(len(df)):
    for v, k in enumerate(df.loc[i, "spec_dict"]):
        if k not in UKS:
            UKS.append(k)

for i in range(len(df)):
    for v, k in enumerate(df.loc[i, "spec_dict2"]):
        if k not in UKS:
            UKS.append(k)

print((UKS))

df = df.drop(columns=["specs", "specs2", "tech1", "tech2"])
df.to_json("Meta_v2.json")
