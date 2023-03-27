# Warehouse
Automation LAB 2022-23 automated warehouse

26/03
Da implementare:

- Gestione cambio modalità. Bug Fixing. ✅

- Allert più sensori attivi ✅ su move2target non dare done 
- Allert posizione stessa con motore attivo da più di  TIMER TIMEOUT ✅ Da rivedere dopo aver aggiunto l'history

- Aggiungere cronologie:
	. Ultimo sensore xogni dof
	. Ultimo motore xogni dof
- Posizione = 0 non dare done --> se motore attivo, aspetta TIMER TIMOUT, se motore non attivo muovi:
	. Se posizione current div da 0 muovi normale
	. Se posizione current = 0 vedi history:
		. Se Ultimo sens div da 0, vedi ultimo motore, muovi.
		. Se no ultimo motore e no ultimo sensore e no current --> Allert: Ultima posizione non riconosciuta su asse (X o Y o Z), muovi in manuale sull'asse (X o Y o Z) e continua a muovere fino a raggiungere una posizione nota (fino alla scomparsa del'allert) [INIZIALIZZAZIONE]


