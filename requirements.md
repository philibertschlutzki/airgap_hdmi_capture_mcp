Anforderungsspezifikation: Autonomer MCP-Agent für gehärtete Air-Gap-Systeme (Vision-HID-Bridge)
1. Einführung und strategische Einordnung
1.1 Ausgangslage und Problemstellung
In der heutigen Cybersicherheitslandschaft gelten sogenannte "Air-Gap"-Systeme – Computer oder Netzwerke, die physisch von unsicheren Netzwerken wie dem Internet oder dem Unternehmens-LAN getrennt sind – als der Goldstandard für den Schutz kritischer Infrastrukturen und hochsensibler Daten. Diese Isolation, oft in industriellen Steuerungssystemen (ICS), militärischen Anlagen oder Root-CA-Umgebungen anzutreffen, stellt jedoch nicht nur eine Barriere für Angreifer dar, sondern auch eine signifikante Hürde für legitime Wartungs-, Überwachungs- und Administrationsaufgaben. Die Annahme, dass physische Trennung absolute Sicherheit garantiert, gilt zunehmend als überholt, da Angriffsvektoren über elektromagnetische Abstrahlung, mobile Datenträger oder Hardware-Implantate die Isolation untergraben können. Gleichzeitig leiden Organisationen unter dem immensen manuellen Aufwand, der für das Patch-Management und die Auditierung dieser isolierten Inseln erforderlich ist.
Herkömmliche Automatisierungslösungen, wie Remote Desktop Protocol (RDP) oder SSH, verletzen per Definition das Air-Gap-Prinzip, da sie Netzwerkverbindungen erfordern. Agentenbasierte Ansätze, die auf dem Zielsystem installiert werden, vergrößern die Angriffsfläche und scheitern oft an strikten Härtungsmaßnahmen wie AppLocker oder deaktivierten USB-Massenspeicher-Treibern. Es besteht daher ein dringender Bedarf an einer externen, nicht-invasiven Automatisierungslösung, die den menschlichen Administrator imitiert ("Human-in-the-Loop"-Simulation), ohne die logische Netzwerktrennung aufzuheben.
1.2 Zielsetzung und Lösungsansatz
Ziel dieser Spezifikation ist die Definition eines autonomen Hard- und Softwaresystems, das administrative Aufgaben auf einem gehärteten Windows-System (Zielsystem) durchführt, indem es die physischen Schnittstellen eines menschlichen Benutzers emuliert: Sehen (Monitorausgabe) und Handeln (Tastatureingabe).
Das vorgeschlagene System, im Folgenden als "Vision-HID-Bridge" bezeichnet, nutzt das Model Context Protocol (MCP) , um eine standardisierte Kommunikationsschicht zwischen einer künstlichen Intelligenz (dem Agenten) und der physischen Hardware zu etablieren. Anstatt proprietäre Schnittstellen zu definieren, fungiert der MCP-Server als Abstraktionsschicht, die visuelle Informationen in Kontext für das Sprachmodell (LLM) umwandelt und dessen textbasierte Handlungsanweisungen in physische HID-Signale (Human Interface Device) übersetzt.
Der Kern des Systems besteht aus einer Hardware-Komponente (Raspberry Pi Zero als HID-Injector und HDMI-Capture-Unit) und einer Software-Architektur, die auf modernen Vision-Language-Modellen (VLMs) basiert, um den Zustand des Zielsystems visuell zu erfassen und zu interpretieren.
1.3 Geltungsbereich (Scope)
Diese Spezifikation deckt die folgenden Bereiche ab:
 * Hardware-Design: Spezifikation der Schnittstelleneinheit (Raspberry Pi Zero, HDMI Capture) und deren physikalische Verbindung unter Berücksichtigung von Stealth-Anforderungen und elektrischer Isolation.
 * Software-Architektur: Definition des MCP-Servers, der MCP-Tools und -Ressourcen sowie der Integrationslogik für OCR (Optical Character Recognition) und VLMs.
 * Interaktionslogik: Spezifikation der Keystroke-Injection-Strategien zur Umgehung von Bot-Erkennungsmechanismen auf gehärteten Windows-Systemen (Admin CLI).
 * Sicherheitsanforderungen: Definition von Maßnahmen zum Selbstschutz des Agenten und zur Verhinderung von Missbrauch (Securing AI Agents).
Ausgeschlossen aus dieser Spezifikation sind die internen Algorithmen der genutzten Large Language Models (z.B. GPT-4o oder Claude 3.5 Sonnet) selbst; diese werden als Black-Box-Komponenten betrachtet, die über standardisierte APIs angesprochen werden.
2. Systemarchitektur und Designprinzipien
2.1 Das MCP-Paradigma in cyber-physischen Systemen
Das Model Context Protocol (MCP) wurde primär entwickelt, um LLMs den Zugriff auf isolierte Datenbestände zu ermöglichen. In diesem Projekt wird das Paradigma erweitert: Der "Datenbestand" ist der physische Zustand des Zielsystems (Bildschirminhalt), und die "Tools" sind physische Aktoren (Tastatur).
Die Architektur folgt dem Client-Host-Server-Modell des MCP :
 * MCP Host/Client: Die Laufzeitumgebung, in der der KI-Agent operiert (z.B. Claude Desktop, eine Python-basierte Agenten-Runtime oder ein LangChain-Konstrukt). Hier findet die kognitive Verarbeitung statt ("Reasoning").
 * MCP Server: Die Brückenkomponente, die auf der Steuereinheit (Control Node) läuft. Sie exponiert die Hardware-Fähigkeiten als standardisierte JSON-RPC-Methoden.
 * Local Resources: Die physischen Geräte (HDMI Capture Card, Raspberry Pi Zero HID Gadget).
Durch diese Entkopplung wird eine hohe Modularität erreicht. Der KI-Agent muss nicht wissen, wie ein Tastendruck elektrisch ausgelöst wird; er ruft lediglich das Tool send_keystrokes auf. Dies reduziert die Komplexität der Agenten-Logik und erhöht die Wartbarkeit.
2.2 Topologische Übersicht
Die Systemtopologie ist strikt in drei Zonen unterteilt, um die Air-Gap-Integrität zu wahren:
| Zone | Komponente | Funktion | Verbindungen |
|---|---|---|---|
| Zone 0 (Target) | Gehärtetes Windows-System | Ziel der Administration. | HDMI Out (zu Zone 1), USB In (von Zone 1). Keine Netzwerkverbindung. |
| Zone 1 (Bridge) | Interface Unit (Pi Zero + Capture Card) | Signalkonvertierung (USB/HDMI ↔ Daten). | USB (zu Zone 0), USB/Serial (zu Zone 2). |
| Zone 2 (Control) | Control Node (Laptop/Edge Device) | Ausführung von MCP Server, OCR, VLM. | USB (zu Zone 1), Optional Netzwerk (zu Cloud LLM). |
Kritischer Design-Hinweis: Es darf keine direkte elektrische Verbindung geben, die eine TCP/IP-Brücke zwischen Zone 0 und Zone 2 ermöglicht (z.B. kein aktiviertes Ethernet-Bridging über den Pi Zero). Die Kommunikation erfolgt ausschließlich unidirektional (Video) bzw. als emulierte HID-Befehle, was das Risiko eines Netzwerkangriffs minimiert.
3. Hardware-Anforderungen (Interface Unit)
Die Hardware-Komponenten bilden die physische Grundlage für die Interaktion. Sie müssen robust, zuverlässig und kompatibel mit Standard-Treibern des Zielsystems sein.
3.1 Keystroke Injection: Raspberry Pi Zero
Der Raspberry Pi Zero (W/2W) wird aufgrund seiner Unterstützung für den USB-Gadget-Modus (OTG) als Aktor gewählt. Im Gegensatz zu Mikrocontrollern wie Arduino bietet er ein vollwertiges Linux-OS, was komplexere Skripte und Pufferung ermöglicht.
3.1.1 USB Gadget Konfiguration (Linux ConfigFS)
Das System muss den libcomposite Treiber und ConfigFS nutzen, um sich flexibel als USB-Gerät zu definieren.
 * ** Emulation:** Der Pi Zero muss sich als Standard "USB Human Interface Device" (Tastatur) ausgeben. Die Nutzung des "Boot Protocol" im USB-Descriptor ist zwingend erforderlich, um auch BIOS/UEFI-Ebenen und BitLocker-Pre-Boot-Authentifizierungen bedienen zu können.
 * ** Identitäts-Spoofing:** Um Whitelisting-Maßnahmen des gehärteten Windows-Systems (z.B. über GPO gesteuerte Installationseinschränkungen für neue Geräte) zu umgehen, müssen Vendor ID (VID) und Product ID (PID) sowie Seriennummern dynamisch konfigurierbar sein. Das System sollte in der Lage sein, IDs gängiger Peripheriehersteller (Dell, HP, Lenovo) zu klonen.
 * ** Stealth-Modus:** Der Pi Zero darf keine seriellen Konsolen oder Netzwerkschnittstellen über den USB-Port exponieren, der mit dem Zielsystem verbunden ist. Dies verhindert, dass das Zielsystem den Pi als "Computer" oder "Massenspeicher" erkennt, was Sicherheitsalarme auslösen würde.
3.1.2 Physische Schnittstelle
 * ** Datenverbindung:** Der Micro-USB "Data"-Port des Pi Zero wird mit dem Zielsystem verbunden.
 * ** Steuerkanal:** Die Kommunikation zwischen dem Control Node (MCP Server) und dem Pi Zero erfolgt idealerweise über die GPIO-Pins (UART/Serial) oder einen separaten USB-Ethernet-Adapter am zweiten USB-Port des Pi, um den Datenpfad zum Target elektrisch zu isolieren. WLAN sollte in Hochsicherheitsbereichen deaktiviert sein (RF-Silence), es sei denn, spezifische Szenarien erlauben dies.
3.2 Visuelle Erfassung: HDMI Capture
Die Capture-Karte ist das "Auge" des Agenten.
 * ** UVC-Kompatibilität:** Die Karte muss den USB Video Class (UVC) Standard unterstützen, um treiberlos unter Linux (Control Node) als /dev/videoX Gerät erkannt zu werden. Dies stellt die Kompatibilität mit Bibliotheken wie OpenCV sicher.
 * ** Auflösung und Signalqualität:** Unterstützung von mindestens 1080p (1920x1080) bei 30fps. Kritisch ist die Unterstützung von 4:4:4 Chroma Subsampling oder zumindest hochwertigem 4:2:2. Bei Standard 4:2:0 Subsampling (häufig bei billigen Capture Cards) wird farbiger Text (z.B. grünes Terminal auf schwarzem Grund) unscharf und ausgefranst, was die OCR-Fehlerrate drastisch erhöht.
 * ** Latenz:** Die Latenz zwischen HDMI-Eingang und Verfügbarkeit des Frames im Userspace des Control Node darf 200ms nicht überschreiten, um die Reaktionszeit des Agenten in interaktiven CLI-Sitzungen akzeptabel zu halten.
4. Software-Spezifikation: Der MCP-Server
Der MCP-Server ist die Kernkomponente auf dem Control Node. Er implementiert die Spezifikation des Model Context Protocol und übersetzt High-Level-Intentionen in Low-Level-Treiberaufrufe.
4.1 Server-Architektur und Technologie
Die Implementierung erfolgt in Python, um die Synergien zwischen dem MCP Python SDK  und Bildverarbeitungsbibliotheken (OpenCV, PyTesseract) zu nutzen.
 * ** Framework:** Nutzung des fastmcp oder mcp Pakets zur Definition des Servers. Der Server muss als persistenter Prozess laufen, der Hardware-Ressourcen (Kamera, serielle Verbindung zum Pi) beim Start initialisiert und offen hält.
 * ** Transport:** Unterstützung von stdio für die lokale Nutzung (z.B. innerhalb von Claude Desktop oder lokalen Agenten-Runtimes) und SSE (Server-Sent Events) über HTTP für verteilte Architekturen.
4.2 Definition der MCP-Tools (Capabilities)
Die folgenden Tools müssen gemäß MCP-Spezifikation exponiert werden. Jedes Tool benötigt ein präzises JSON-Schema.
4.2.1 Tool: capture_screen
Dieses Tool liefert den aktuellen visuellen Zustand.
 * Beschreibung: Erfasst einen Frame von der Capture Card.
 * Schema-Definition:
   {
  "name": "capture_screen",
  "description": "Captures the current screen content from the target system via HDMI.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "mode": {
        "type": "string",
        "enum": ["raw_base64", "ocr_text", "analysis"],
        "description": "Return mode: raw image, extracted text via OCR, or VLM analysis."
      },
      "region": {
        "type": "array",
        "items": { "type": "integer" },
        "minItems": 4,
        "maxItems": 4,
        "description": "[x, y, width, height] - Optional region of interest."
      }
    }
  }
}

 * Funktionale Anforderung: Im Modus ocr_text muss der Server vor der Texterkennung Bildverbesserungen durchführen (Invertierung, Kontrastanhebung), um die Lesbarkeit von Terminal-Schriften zu optimieren.
4.2.2 Tool: inject_keystrokes
Dieses Tool ermöglicht die Texteingabe.
 * Beschreibung: Sendet Text oder Tastenbefehle an das Zielsystem.
 * Schema-Definition:
   {
  "name": "inject_keystrokes",
  "description": "Types text or key combinations into the target system.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "text": {
        "type": "string",
        "description": "The string to type. Supports special keys via format like {ENTER}, {TAB}."
      },
      "delay_ms": {
        "type": "integer",
        "description": "Delay between keystrokes in ms. Use >50 for realism.",
        "default": 20
      }
    },
    "required": ["text"]
  }
}

 * Funktionale Anforderung: Das Tool muss eine Mapping-Logik enthalten, die Unicode-Zeichen in die entsprechenden Scancodes des Ziel-Layouts (z.B. German ISO) übersetzt. Ein simples Senden von ASCII-Codes ist bei HID nicht ausreichend; es müssen Modifier-States (Shift, AltGr) explizit verwaltet werden (z.B. '@' auf deutscher Tastatur erfordert AltGr+Q).
4.2.3 Tool: execute_shortcut
Für spezielle Systembefehle, die nicht über reinen Text abbildbar sind.
 * Beschreibung: Führt Tastenkombinationen wie Ctrl+Alt+Del oder Win+R aus.
 * Parameter: modifiers (Liste von Strings:), key (String).
 * Implementierung: Direktes Schreiben von HID-Reports an /dev/hidg0 auf dem Pi Zero, wobei das erste Byte die Bitmaske für Modifier enthält.
4.3 Definition der MCP-Ressourcen
Ressourcen bieten dem LLM direkten Zugriff auf Daten, ohne Tools auszuführen ("Lesen" vs. "Handeln").
 * ** Ressource system://screen/latest:** Ein URI, der immer das aktuellste Bild bereitstellt. Der Agent kann diese Ressource pollen oder abonnieren.
 * ** Ressource system://logs/ocr:** Ein Log-Puffer der letzten 100 Zeilen erkannten Textes. Dies ermöglicht dem Agenten ein "Kurzzeitgedächtnis" für Bildschirminhalte, die bereits weggescrollt sind.
5. Vision-Pipeline und Kognitive Verarbeitung
Die Fähigkeit des Systems, auf das gehärtete CLI (Command Line Interface) zu reagieren, hängt kritisch von der Qualität der visuellen Verarbeitung ab.
5.1 Herausforderungen der CLI-OCR
Windows Admin CLIs (cmd.exe, PowerShell) nutzen standardmäßig Monospace-Schriften auf dunklem Hintergrund. Standard-OCR-Modelle sind oft auf schwarzen Text auf weißem Papier (Dokumente) trainiert.
 * ** Pre-Processing Pipeline:** Vor der OCR-Anwendung müssen folgende Schritte durchlaufen werden:
   * Grayscale Conversion: Reduktion auf Graustufen.
   * Inversion: Umkehrung der Farben (Weiß auf Schwarz -> Schwarz auf Weiß), da Tesseract dies bevorzugt.
   * Rescaling: Vergrößerung des Bildes (Upsampling) um Faktor 2-3x, da CLI-Schriften bei 1080p oft nur wenige Pixel breit sind und Antialiasing die Kanten für OCR undeutlich macht.
   * Thresholding: Binarisierung (Otsu's Binarization) zur Entfernung von Hintergrundrauschen (z.B. Transparenzeffekte in modernen Terminals).
5.2 OCR-Engine Auswahl
 * Primär: Tesseract OCR (v5 mit LSTM). Es ist Open-Source, lokal ausführbar (wichtig für Air-Gap/Datenschutz) und bietet spezifische Modi für Monospace-Schriften (--psm 6 für einheitliche Textblöcke).
 * Sekundär (Fallback): Local Vision Language Models (VLM) wie LLaVA (Large Language-and-Vision Assistant) oder Qwen-VL-Chat.
   * Einsatz: Wenn Tesseract versagt (z.B. bei komplexen ASCII-Art-Logos, UAC-Dialogen oder überlappenden Fenstern), wird ein Screenshot an das VLM gesendet mit dem Prompt: "Extrahiere den genauen Text und beschreibe den Systemzustand".
   * Performance: VLMs haben eine höhere Latenz (Sekunden vs. Millisekunden bei Tesseract). Daher sollte Tesseract der Standard für den schnellen Regelkreis sein.
5.3 OODA-Loop (Observe-Orient-Decide-Act)
Der Agent darf nicht "blind" arbeiten. Er muss in einer geschlossenen Regelschleife operieren.
 * Observe: capture_screen aufrufen.
 * Orient: OCR-Ergebnis analysieren. Prüfen auf Schlüsselwörter (Prompts wie C:\>, Fehlercodes, "Press any key").
 * Decide: LLM vergleicht Ist-Zustand mit Ziel.
   * Beispiel: Ziel ist "Ordner löschen". Ist-Zustand zeigt "Access Denied". Entscheidung: "Versuche takeown Befehl".
 * Act: inject_keystrokes ausführen.
 * Verify: Erneuter capture_screen nach Verzögerung, um zu prüfen, ob die Eingabe erschienen ist (Echo-Check).
6. Zielsystem-Interaktion: Gehärtetes Windows
Gehärtete Windows-Systeme (gemäß CIS Benchmarks oder BSI-Grundschutz) stellen spezifische Hindernisse dar, die das Design beeinflussen.
6.1 Umgehung von USB-Restriktionen
Viele Hochsicherheitsumgebungen blockieren USB-Massenspeicher (DLP - Data Loss Prevention) und unbekannte Geräte.
 * ** HID-only Ansatz:** Der Agent verlässt sich ausschließlich auf HID. HID-Geräte (Tastaturen/Mäuse) können selten komplett blockiert werden, da das System sonst unbedienbar wäre. Dennoch existieren Whitelists für VIDs/PIDs.
 * ** Driverless Operation:** Der Pi Zero muss Standard-Klassen-Treiber nutzen (kbdhid.sys). Es darf keine Installation von Spezialtreibern auf dem Target erforderlich sein.
6.2 Anti-Automatisierungs-Erkennung
Fortgeschrittene Endpoint Detection & Response (EDR) Systeme können extrem schnelle Tastatureingaben als "Script-Based Attack" (wie Rubber Ducky) klassifizieren.
 * ** Humanisierung der Eingabe:**
   * Jitter: Die Verzögerung zwischen Tastenanschlägen darf nicht konstant sein (z.B. exakt 10ms). Sie muss einer Gauß-Verteilung folgen (z.B. Mittelwert 80ms, Standardabweichung 30ms).
   * Burst-Typing: Simulation von schnellen Bursts (geübter Tipper) gefolgt von kurzen Denkpausen.
   * Behavioral Libraries: Implementierung von Bibliotheken wie bezier für Mausbewegungen (falls Maus genutzt wird) oder spezialisierte Python-Bibliotheken zur Generierung realistischer Timing-Profile.
6.3 Interaktion mit der Admin CLI
Die Interaktion mit cmd oder powershell erfordert präzises Kontextverständnis.
 * ** Prompt-Erkennung:** Der Agent muss das Ende eines Befehls erkennen. Da CLI-Operationen synchron blockieren, muss der Agent auf das Wiedererscheinen des Prompts (z.B. PS C:\Windows\system32>) warten, bevor der nächste Befehl gesendet wird. Ein einfaches sleep(5) ist unzuverlässig.
 * ** Paging-Handling:** Lange Ausgaben (z.B. dir /s) führen zu "Press any key to continue" oder Scrollen. Der Agent muss dies erkennen und ggf. die Leertaste senden, um mehr Text zu erhalten.
7. Sicherheitsarchitektur und Risikomanagement
Ein System, das dazu dient, Sicherheitsbarrieren (Air Gap) zu überbrücken, stellt selbst ein hohes Risiko dar ("Dual-Use Technology").
7.1 Selbstschutz des Implantats
 * ** Read-Only Filesystem:** Der Raspberry Pi Zero sollte so konfiguriert sein, dass sein Root-Dateisystem im Read-Only-Modus läuft (OverlayFS). Dies verhindert, dass Malware vom Zielsystem (falls dieses kompromittiert ist und versucht, angeschlossene USB-Geräte zu infizieren) sich auf dem Agenten persistiert.
 * ** Einweg-Datenfluss (Logisch):** Obwohl USB bidirektional ist, sollte die logische Architektur so ausgelegt sein, dass keine Dateien vom Target auf den Control Node übertragen werden, außer den Screenshots. Dies verhindert die Exfiltration von Daten über den Agenten, falls der Control Node kompromittiert wird.
7.2 Authentifizierung und Zugriffskontrolle
 * ** MCP-Auth:** Der Zugriff auf den MCP-Server muss authentifiziert sein. Falls Control Node und Agent-Runtime getrennt sind (Netzwerk), ist mTLS (Mutual TLS) oder zumindest Token-basierte Auth zwingend erforderlich, um zu verhindern, dass ein unautorisierter Prozess im Netzwerk Befehle an das Target sendet.
 * ** "Kill Switch":** Es muss eine physische oder softwareseitige Not-Aus-Funktion geben, die die USB-Verbindung sofort trennt (z.B. echo "" > /dev/hidg0 oder modprobe -r g_hid), falls der Agent fehlfunktioniert (z.B. Endlosschleife beim Tippen).
7.3 Datenschutz (Redaction)
 * ** PII-Filterung:** Wenn Screenshots an ein Cloud-LLM gesendet werden müssen (was bei Air-Gap eigentlich vermieden werden sollte), müssen sensitive Daten (Passwörter, IP-Adressen) vorher lokal maskiert werden. Bevorzugt wird die lokale Verarbeitung durch On-Premises LLMs.
8. Qualitätsmanagement und Teststrategie
8.1 Hardware-in-the-Loop (HIL) Testing
Da das System mit physischer Hardware interagiert, reichen reine Unit-Tests nicht aus.
 * ** Teststand:** Aufbau eines HIL-Teststands, bei dem der Pi Zero an einen Test-PC angeschlossen ist, dessen Bildschirminhalt bekannt und kontrollierbar ist.
 * ** OCR-Benchmark:** Systematische Tests der OCR-Erkennungsrate mit verschiedenen CLI-Farbschemata (PowerShell Blau, CMD Schwarz, Hacker Grün) und Schriftarten. Ziel: >99% Zeichengenauigkeit bei Code/Befehlen.
8.2 Offene Punkte und Rückfragen (Design Assumptions)
Gemäß der Aufgabenstellung ("Stelle falls nötig Rückfragen") sind folgende Aspekte in der Designphase zu klären, wurden hier aber mit Annahmen belegt:
 * Stromversorgung: Wird der Pi Zero vom USB-Port des Targets gespeist?
   * Annahme: Ja. Risiko: Manche gehärteten USB-Ports schalten bei Überlast ab. Der Pi Zero muss im Low-Power-Mode laufen (HDMI/LEDs off).
 * BIOS-Zugriff: Ist Zugriff auf BIOS/UEFI notwendig?
   * Annahme: Ja. Dies erfordert, dass das HID-Gadget das "Boot Protocol" unterstützt und schnell genug nach Power-On initialisiert (Startzeitoptimierung des Linux-Bootprozesses auf <5s erforderlich).
 * Netzwerk im Serverraum: Darf der Control Node WLAN nutzen?
   * Annahme: Nein, striktes RF-Verbot. Kommunikation Pi <-> Control Node via USB-Ethernet oder seriell über Kabel.
9. Implementierungs-Roadmap
Die Entwicklung gliedert sich in folgende Phasen:
| Phase | Aktivität | Fokus |
|---|---|---|
| 1 | Hardware-Integration | Setup Pi Zero Gadget Mode, ConfigFS Skripte, Latenzmessung HDMI. |
| 2 | MCP Server Core | Implementierung der Python-Basis, JSON-RPC Handling, Integration Capture & HID. |
| 3 | Vision-Pipeline | Training/Config von Tesseract für CLI, Integration OpenCV Pre-Processing. |
| 4 | Agenten-Entwicklung | Erstellung der System Prompts für das LLM, Definition der OODA-Logik. |
| 5 | Härtung & Review | Security Audit des Codes, Implementierung Jitter/Stealth, Read-Only FS. |
10. Fazit
Die Vision-HID-Bridge stellt eine innovative Lösung dar, um die Vorteile moderner generativer KI (Agentic AI) in hochsensible, isolierte Umgebungen zu bringen, ohne deren Sicherheitsarchitektur grundlegend zu kompromittieren. Durch die Nutzung des Model Context Protocol wird eine zukunftssichere, standardisierte Schnittstelle geschaffen, die es erlaubt, die zugrundeliegende KI (das "Gehirn") auszutauschen, während die Hardware-Schnittstelle (der "Körper") konstant bleibt.
Die größte technische Herausforderung liegt in der Zuverlässigkeit der visuellen Rückkopplungsschleife (OCR-Fehler) und der Unauffälligkeit der HID-Injektion. Durch die in dieser Spezifikation definierten Anforderungen an Hardware-Qualität, Bildvorverarbeitung und heuristische Humanisierung wird ein robustes Fundament für die Umsetzung gelegt. Das System ermöglicht somit eine "virtuelle Hands-on"-Administration, die Effizienzsteigerungen verspricht, während der Air-Gap physikalisch intakt bleibt.
Ende der Spezifikation.
