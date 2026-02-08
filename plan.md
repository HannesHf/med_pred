# EDA
## versterbende patienten
PS C:\Users\hhaef\Hannes\med_pred> uv run .\eda\check_labels.py
📊 Prüfe Label-Verteilung...
   label   count  percentage
0      0  291996   89.253379
1      1   35158   10.746621

1 -> Tod

Kann man prognostizieren um einen Sterbescore zu bekommen


## Entlassungsinformationen
 es gibt auch entlassungsinformationen, die nutzbar sind um mehr auf Lebensqualität und Zustand zu fokussieren

PS C:\Users\hhaef\Hannes\med_pred> uv run eda\check_outcomes.py

🏥 Analysiere Entlassungs-Orte (Proxy für Lebensqualität)...

Anzahl Überlebende in Analyse: 534227
------------------------------------------------------------
ENTLASSUNG NACH                          | ANZAHL     | ANTEIL %
------------------------------------------------------------
HOME                                     | 194116     | 36.3%
None                                     | 149656     | 28.0%
HOME HEALTH CARE                         | 99296      | 18.6%
SKILLED NURSING FACILITY                 | 52642      | 9.9%
REHAB                                    | 13842      | 2.6%
CHRONIC/LONG TERM ACUTE CARE             | 8121       | 1.5%
HOSPICE                                  | 5375       | 1.0%
AGAINST ADVICE                           | 3393       | 0.6%
PSYCH FACILITY                           | 2964       | 0.6%
ACUTE HOSPITAL                           | 2332       | 0.4%
OTHER FACILITY                           | 1591       | 0.3%
ASSISTED LIVING                          | 622        | 0.1%
DIED                                     | 227        | 0.0%
HEALTHCARE FACILITY                      | 50         | 0.0%


# Vorgehen
1 Modell für Todesrisiko
2 Modell für Entlassung
3 generisches Modell - BERT basiert, aus dem man die Wahrscheinlichkeit für jedes Event ableiten kann (BIG CHALLENGE)


## Modell für Todesrisiko
Ein Modell, das mit allen Informationen den Tod vorhersagt, ist mäßig beeindruckend und kaum hilfreich. Validierung während des Aufenthalts ist essenziell! Dafür cutten der aufnethalte nach jedem token und Neuberechnung des Risikos an dieser Stelle. Wie umsetzen und wie aggregiert messen? Was ist die Wahrheit?

macht dieser Ansatz Sinn? Was sind objektive Stärken und Schwächen?
- mglw werden anfängliche Informationen für das Sterberisiko überbewertet, da das finale Outcome nicht zwingend korrekt sein muss
- was ist mit patienten mit mehreren aufenthalten?

### analyse wie verläuft das todesrisiko während der aufenthalte verläuft
   Werte: AUROC
-> 20%  0.7321
-> 40%  0.7127
-> 60%  0.6958
-> 80%  0.7007
-> 100%  0.7211
kein größerer Unterschied -> Cases mit Schwankungen ansehen.

-> streamlit app -> im eyeballing sind einzelne verläufe recht klar mit ansteigendem und sinkendem risiko und differenzieren das risiko. die abbildung der testergebnisse scheint aber nicht so gut zu sein -> viele tests in Folge sind abnormal -> ausdifferenzieren -> feinere skala oder komplett anders encoden
Beispiel: 
🧪 Labor: 51266_abnormal
🧪 Labor: 51265_abnormal
-> Inhalt Token + Value Token

es waren nur tests mit abnormalen ergebnisse enthalten


am anfang steht nicht die aufnahme -> korrekt?
