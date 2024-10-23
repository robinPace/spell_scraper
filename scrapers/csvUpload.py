import csv
import pandas as pd
import mysql.connector

cnx = mysql.connector.connect(
    user = "root",
    password = "Rp12073419r$",
    host = "localhost",
    database = "spells"
)

if cnx.is_connected():
    print("connected")

    cursor = cnx.cursor()

    data = pd.read_csv(r"C:\Users\robin\CS\myWork\dndNew\scraper\spells.csv")
    df = pd.DataFrame(data)

    cursor.execute("DROP TABLE IF EXISTS spells.spelllist")

    cursor.execute(
        """
        CREATE TABLE spelllist (
        Name VARCHAR(255),
        Source VARCHAR(255),
        Type VARCHAR(255),
        Level INT,
        Cast_Time VARCHAR(255),
        Spell_Range VARCHAR(255),
        Components VARCHAR(500),
        Verbal TINYINT(1),
        Somatic TINYINT(1),
        Material TINYINT(1),
        Material_Cost VARCHAR(255),
        Duration VARCHAR(255),
        Concentration TINYINT(1),
        Description VARCHAR(5000),
        AOE TINYINT(1),
        AOE_Size VARCHAR(255),
        AOE_Shape VARCHAR(255),
        Saving_Throw TINYINT(1),
        Saving_Throw_Type VARCHAR(255),
        Damage VARCHAR(255),
        Damage_Type VARCHAR(255),
        Attack_Roll TINYINT(1),
        Healing TINYINT(1),
        Pushing TINYINT(1),
        Push_Distance VARCHAR(255),
        At_Higher_Levels VARCHAR(5000),
        Spell_Lists VARCHAR(255),
        More TINYINT(1)
        )
        """
    )


    for row in df.itertuples():
        sql = """
                INSERT INTO spelllist (Name, Source, Type, Level, Cast_Time, Spell_Range, Components, Verbal, Somatic, Material, Material_Cost, Duration, Concentration, 
                Description, AOE, AOE_Size, AOE_Shape, Saving_Throw, Saving_Throw_Type, Damage, Damage_Type, Attack_Roll, Healing, Pushing, Push_Distance, At_Higher_Levels, 
                Spell_Lists, More) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        
        vals = (row.Name, row.Source, row.Type, row.Level, row.Cast_Time, row.Range, row.Components, row.Verbal, row.Somatic, row.Material, row.Material_Cost, row.Duration, row.Concentration, row.Description, row.AOE, row.AOE_size, row.AOE_shape, row.Saving_Throw, row.Saving_Throw_Type, row.Damage, row.Damage_Type, row.Attack_Roll, row.Healing, row.Pushing, row.Push_Distance, row.At_Higher_Levels, row.Spell_Lists, row.More)
        cursor.execute(sql, vals)

        cnx.commit()
        print(row.Name, "Inserted")