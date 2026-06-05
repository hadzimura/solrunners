# Prameny života

# Princip

Celé řešení se skládá z pěti (mini)počítačů značky `Raspberry Pi`, vzájemně propojených privátní wifi sítí. Pro účely diskuse (přesněji: monologu) budeme těmto přístrojům říkat `krabička`. Všechny `krabičky` umí přehrávat zvuky, tři pak navíc mají připojenou obrazovku. Většina `krabiček` je vybavena buď senzorem _Pohybu_ a/nebo _Vzdálenosti_, naměřené hodnoty sdílí s takzvanou **hlavní** `krabičkou`. Je to celkově taková zabezpečovačka s výhodami. Rozložení krabiček v prostoru vypadá následovně: 

| room | RPi model | motion | distance | speakers | display |
|------|-----------|--------|----------|----------|---------|
| 1    | 3         | o      | x        | o        | x       | 
| 3    | 2         | o      | x        | o        | x       | 
| 3    | 5         | x      | o        | o        | o       | 
| 4    | 5         | ?      | ?        | ?        | o       | 
| 5    | 5         | o      | x        | o        | o (2)   |



## Entropie


Hlavní atrakcí celého kolotočde je bratru pětiminutové video **Entropie**, umístěné ve třetí místnosti. V okamžiku jeho  

# Audio

Sounds are played independently of video tracks and use `pygame` library. The player uses `StaticSource` resource type that loads all the audio tracks into the memory and allows dynamic mixing of the master track: that's why all the tracks consist of separate 

One of the nodes acts as a `master` node and collects all the presence data. 