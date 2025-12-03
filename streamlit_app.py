import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time
from functools import wraps
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

st.set_page_config(page_title="NYZTrade Smallcap", page_icon="🎯", layout="wide")

def check_password():
    def password_entered():
        username = st.session_state["username"].strip().lower()
        password = st.session_state["password"]
        users = {"demo": "demo123", "premium": "premium123", "niyas": "nyztrade123"}
        if username in users and password == users[username]:
            st.session_state["password_correct"] = True
            st.session_state["authenticated_user"] = username
            del st.session_state["password"]
            return
        st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        st.markdown("<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3rem; border-radius: 20px; text-align: center;'><h1 style='color: white;'>NYZTrade Smallcap Pro</h1></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.button("Login", on_click=password_entered, use_container_width=True)
            st.info("demo/demo123 | premium/premium123")
        return False
    elif not st.session_state["password_correct"]:
        st.error("Incorrect credentials")
        return False
    return True

if not check_password():
    st.stop()

st.markdown("""
<style>
.main-header{background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);padding:2.5rem;border-radius:20px;text-align:center;color:white;margin-bottom:2rem;box-shadow: 0 10px 30px rgba(67, 233, 123, 0.3);}
.fair-value-box{background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);padding:2rem;border-radius:15px;text-align:center;color:white;margin:2rem 0;box-shadow: 0 10px 30px rgba(250, 112, 154, 0.3);}
.rec-strong-buy{background: linear-gradient(135deg, #00C853 0%, #64DD17 100%);color:white;padding:2rem;border-radius:15px;text-align:center;font-size:2rem;font-weight:bold;}
.rec-buy{background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);color:white;padding:2rem;border-radius:15px;text-align:center;font-size:2rem;font-weight:bold;}
.rec-hold{background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);color:white;padding:2rem;border-radius:15px;text-align:center;font-size:2rem;font-weight:bold;}
.rec-avoid{background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);color:white;padding:2rem;border-radius:15px;text-align:center;font-size:2rem;font-weight:bold;}
</style>
""", unsafe_allow_html=True)

SMALLCAP_STOCKS = {
    "Engineering Manufacturing 1": {
        "AARTISURF.NS":"Aarti Surfactants","ABSORB.NS":"Absorb Plus","ACCELYA.NS":"Accelya Kale","ACCURACY.NS":"Accuracy Shipping",
        "ACRYSIL.NS":"Acrysil","ADVENZYMES.NS":"Advanced Enzymes","AEROFLEX.NS":"Aeroflex Industries","AETHER.NS":"Aether Industries",
        "AGCNET.NS":"AGC Networks","AHLEAST.NS":"Asian Hotels East","AHLUCONT.NS":"Ahluwalia Contracts","AIAENG.NS":"AIA Engineering",
        "AIIL.NS":"Ashapura Intimates","AIRAN.NS":"Airan Ltd","AKASH.NS":"Akash Infra-Projects","AKSHARCHEM.NS":"Akshar Chem",
        "AKZOINDIA.NS":"Akzo Nobel India","ALEMBICLTD.NS":"Alembic Pharma","ALICON.NS":"Alicon Castalloy","ALKALI.NS":"Alkali Metals",
        "ALPA.NS":"Alpa Laboratories","ALPHAGEO.NS":"Alphageo India","ALPSINDUS.NS":"Alps Industries","AMARAJABAT.NS":"Amara Raja Energy"
    },
    "Engineering Manufacturing 2": {
        "AMBER.NS":"Amber Enterprises","AMIABLE.NS":"Amiable Logistics","AMJLAND.NS":"AMJ Land Holdings","AMRUTANJAN.NS":"Amrutanjan Health",
        "ANANTRAJ.NS":"Anant Raj","ANDHRSUGAR.NS":"Andhra Sugars","ANGELONE.NS":"Angel One","ANMOL.NS":"Anmol Industries",
        "ANUP.NS":"Anupam Rasayan","APARINDS.NS":"Apar Industries","APCL.NS":"Anjani Portland","APCOTEXIND.NS":"Apcotex Industries",
        "APEX.NS":"Apex Frozen Foods","APLAPOLLO.NS":"APL Apollo Tubes","APOLLO.NS":"Apollo Micro Systems","APOLLOPIPE.NS":"Apollo Pipes",
        "APOLLOTYRE.NS":"Apollo Tyres","APTECHT.NS":"Aptech","ARASU.NS":"Arasu Cable","ARCHIDPLY.NS":"Archidply Industries",
        "ARCHIES.NS":"Archies Ltd","ARL.NS":"Apar Industries","ARMANFIN.NS":"Arman Financial","ARROWGREEN.NS":"Arrow Greentech"
    },
    "Engineering Manufacturing 3": {
        "ARSHIYA.NS":"Arshiya","ARTNIRMAN.NS":"Art Nirman","ARVINDFASN.NS":"Arvind Fashions","ASAHIINDIA.NS":"Asahi India Glass",
        "ASAHISONG.NS":"Asahi Songwon","ASAL.NS":"Automotive Stampings","ASALCBR.NS":"Associated Alcohols","ASHIANA.NS":"Ashiana Housing",
        "ASHIMASYN.NS":"Ashima Ltd","ASHOKA.NS":"Ashoka Buildcon","ASHOKLEY.NS":"Ashok Leyland","ASIANENE.NS":"Asian Energy Services",
        "ASIANHOTNR.NS":"Asian Hotels North","ASIANPAINT.NS":"Asian Paints","ASPINWALL.NS":"Aspinwall","ASTEC.NS":"Astec LifeSciences",
        "ASTERDM.NS":"Aster DM Healthcare","ASTRAL.NS":"Astral Ltd","ASTRAMICRO.NS":"Astra Microwave","ASTRAZEN.NS":"AstraZeneca Pharma",
        "ATAM.NS":"Atam Valves","ATNINTER.NS":"ATN International","ATUL.NS":"Atul Ltd","ATULAUTO.NS":"Atul Auto"
    },
    "Engineering Manufacturing 4": {
        "AURIONPRO.NS":"Aurionpro Solutions","AUSOMENT.NS":"Ausom Enterprise","AUSTRAL.NS":"Austral Coke","AUTOAXLES.NS":"Automotive Axles",
        "AUTOIND.NS":"Autoline Industries","AVALON.NS":"Avalon Technologies","AVANTIFEED.NS":"Avanti Feeds","AVTNPL.NS":"AVT Natural Products",
        "AWL.NS":"Adani Wilmar","AXISCADES.NS":"Axiscades Engineering","AXISGOLD.NS":"Axis Gold","AYMSYNTEX.NS":"AYM Syntex",
        "AZAD.NS":"Azad Engineering","BAGFILMS.NS":"BAG Films","BAJAJELEC.NS":"Bajaj Electricals","BAJAJHIND.NS":"Bajaj Hindusthan Sugar",
        "BALAJITELE.NS":"Balaji Telefilms","BALAXI.NS":"Balaxi Ventures","BALKRISHNA.NS":"Balkrishna Paper","BALMLAWRIE.NS":"Balmer Lawrie",
        "BALPHARMA.NS":"Bal Pharma","BANCOINDIA.NS":"Banco Products","BANG.NS":"Bang Overseas","BANKBARODA.NS":"Bank of Baroda"
    },
    "Chemicals Pharmaceuticals 1": {
        "BANKINDIA.NS":"Bank of India","BANSWRAS.NS":"Banswara Syntex","BARBEQUE.NS":"Barbeque Nation","BASF.NS":"BASF India",
        "BATAINDIA.NS":"Bata India","BBOX.NS":"Black Box","BBL.NS":"Bharat Bijlee","BBTC.NS":"Bombay Burmah",
        "BCG.NS":"Brightcom Group","BCP.NS":"Banco Products","BDL.NS":"Bharat Dynamics","BEEKAY.NS":"Beekay Steel",
        "BEL.NS":"Bharat Electronics","BELSTAR.NS":"Belstar Microfinance","BEML.NS":"BEML","BEPL.NS":"Bhansali Engineering",
        "BERGEPAINT.NS":"Berger Paints","BFINVEST.NS":"BF Investment","BGRENERGY.NS":"BGR Energy Systems","BHAGERIA.NS":"Bhageria Industries",
        "BHAGYANGR.NS":"Bhagiradha Chemicals","BHANDARI.NS":"Bhandari Hosiery","BHARATFORG.NS":"Bharat Forge","BHARATGEAR.NS":"Bharat Gears"
    },
    "Chemicals Pharmaceuticals 2": {
        "BHARATWIRE.NS":"Bharat Wire Ropes","BHARTIARTL.NS":"Bharti Airtel","BHEL.NS":"BHEL","BILENERGY.NS":"Bil Energy Systems",
        "BIOCON.NS":"Biocon","BIRLACABLE.NS":"Birla Cable","BIRLAMONEY.NS":"Aditya Birla Money","BIRLACORPN.NS":"Birla Corporation",
        "BIRLATYRE.NS":"Birla Tyres","BKM.NS":"Bkmindspace","BLACKROSE.NS":"Blackrose Industries","BLAL.NS":"BEML Land Assets",
        "BLISSGVS.NS":"Bliss GVS Pharma","BLKASHYAP.NS":"B L Kashyap","BLUEBLENDS.NS":"Blue Blends","BLUECOAST.NS":"Blue Coast Hotels",
        "BLUEDART.NS":"Blue Dart Express","BLUEJET.NS":"Blue Jet Healthcare","BLUESTARCO.NS":"Blue Star","BODALCHEM.NS":"Bodal Chemicals",
        "BOMDYEING.NS":"Bombay Dyeing","BOROLTD.NS":"Borosil Ltd","BOSCHLTD.NS":"Bosch","BPCL.NS":"BPCL"
    },
    "Chemicals Pharmaceuticals 3": {
        "BRFL.NS":"Bombay Rayon","BRIGADE.NS":"Brigade Enterprises","BRITANNIA.NS":"Britannia","BRO.NS":"Brigade Road",
        "BSE.NS":"BSE Ltd","BSHSL.NS":"Bombay Super Hybrid","BSL.NS":"BSL Ltd","BSOFT.NS":"Birlasoft",
        "BTML.NS":"Bodal Trading","BURNPUR.NS":"Burnpur Cement","BUTTERFLY.NS":"Butterfly Gandhimathi","CADILAHC.NS":"Cadila Healthcare",
        "CADSYS.NS":"Cadsys India","CALSOFT.NS":"California Software","CAMLINFINE.NS":"Camlin Fine Sciences","CAMPUS.NS":"Campus Activewear",
        "CANBK.NS":"Canara Bank","CANFINHOME.NS":"Can Fin Homes","CANTABIL.NS":"Cantabil Retail","CAPF.NS":"Capital First",
        "CAPLIPOINT.NS":"Caplin Point","CAPTRUST.NS":"Capital Trust","CARBORUNIV.NS":"Carborundum Universal","CARERATING.NS":"CARE Ratings"
    },
    "Chemicals Pharmaceuticals 4": {
        "CARGEN.NS":"Cargen Drugs","CARYSIL.NS":"Carysil","CASTROLIND.NS":"Castrol India","CCCL.NS":"Consolidated Construction",
        "CCL.NS":"CCL Products","CDSL.NS":"CDSL","CEATLTD.NS":"CEAT","CELEBRITY.NS":"Celebrity Fashions",
        "CELLO.NS":"Cello World","CENTENKA.NS":"Century Enka","CENTUM.NS":"Centum Electronics","CENTURY.NS":"Century Textiles",
        "CENTURYPLY.NS":"Century Plyboards","CERA.NS":"Cera Sanitaryware","CEREBRAINT.NS":"Cerebra Integrated","CESC.NS":"CESC",
        "CGCL.NS":"Capri Global","CGPOWER.NS":"CG Power","CHAMBLFERT.NS":"Chambal Fertilizers","CHEMBOND.NS":"Chembond Chemicals",
        "CHEMCON.NS":"Chemcon Speciality","CHEMFAB.NS":"Chemfab Alkalis","CHEMPLASTS.NS":"Chemplast Sanmar","CHENNPETRO.NS":"Chennai Petroleum"
    },
    "Textiles Consumer Goods 1": {
        "CHOLAFIN.NS":"Cholamandalam Investment","CHOLAHLDNG.NS":"Cholamandalam Financial","CIEINDIA.NS":"CIE Automotive","CIGNITITEC.NS":"Cigniti Technologies",
        "CINELINE.NS":"Cineline India","CINEVISTA.NS":"Cinevista","CIPLA.NS":"Cipla","CLNINDIA.NS":"Clariant Chemicals",
        "CLSEL.NS":"Chaman Lal Setia","CMICABLES.NS":"CMI Ltd","CMNL.NS":"CMI Ltd","CMDL.NS":"CMDL",
        "COALINDIA.NS":"Coal India","COASTCORP.NS":"Coastal Corporation","COFFEEDAY.NS":"Coffee Day Enterprises","COFORGE.NS":"Coforge",
        "COLPAL.NS":"Colgate Palmolive","COMPINFO.NS":"Compuage Infocom","COMPUSOFT.NS":"Compucom Software","CONCOR.NS":"Container Corporation",
        "CONFIPET.NS":"Confidence Petroleum","CONSOFINVT.NS":"Consolidated Finvest","CONTROLS.NS":"Control Print","COOKCAST.NS":"Cookcast"
    },
    "Textiles Consumer Goods 2": {
        "CORALFINAC.NS":"Coral India Finance","CORDSCABLE.NS":"Cords Cable","COROMANDEL.NS":"Coromandel International","COROENGG.NS":"Coromandel Engineering",
        "CORPBANK.NS":"Corporation Bank","COSMOFILMS.NS":"Cosmo Films","COUNCODOS.NS":"Country Condo's","CPSEETEC.NS":"CPS EeeTech",
        "CREATIVE.NS":"Creative Newtech","CREDITACC.NS":"CreditAccess Grameen","CREATIVEYE.NS":"Creative Eye","CREST.NS":"Crest Ventures",
        "CRIMSONLOG.NS":"Crimson Logistics","CRISIL.NS":"CRISIL","CROMPTON.NS":"Crompton Greaves","CROSSING.NS":"Crossing Republic",
        "CRSBWARDR.NS":"CRISIL Board","CSB.NS":"CSB Bank","CUBEXTUB.NS":"Cubex Tubings","CUMMINSIND.NS":"Cummins India",
        "CUREXAUTO.NS":"Curex Pharmaceuticals","CURATECH.NS":"Cura Technologies","CUB.NS":"City Union Bank","CYBERTECH.NS":"Cybertech Systems"
    },
    "Textiles Consumer Goods 3": {
        "CYBERMEDIA.NS":"Cybermedia India","CYIENT.NS":"Cyient","DABUR.NS":"Dabur India","DAICHISANK.NS":"Daiichi Sankyo",
        "DALMIASUG.NS":"Dalmia Bharat Sugar","DANGEE.NS":"Dangee Dums","DATAMATICS.NS":"Datamatics Global","DATAPATTNS.NS":"Data Patterns",
        "DBOL.NS":"Dhampur Bio Organics","DBL.NS":"Dilip Buildcon","DBREALTY.NS":"DB Realty","DBSTOCKBRO.NS":"DB Stock Brokers",
        "DCAST.NS":"Diecast","DCB.NS":"DCB Bank","DCBBANK.NS":"DCB Bank","DCHL.NS":"Deccan Chronicle",
        "DCM.NS":"DCM Ltd","DCMSHRIRAM.NS":"DCM Shriram","DCMSRL.NS":"DCM Shriram","DCW.NS":"DCW Ltd",
        "DCXINDIA.NS":"DCX Systems","DDL.NS":"Dhunseri Ventures","DEBOCK.NS":"De Nora India","DEEPAKFERT.NS":"Deepak Fertilizers"
    },
    "Textiles Consumer Goods 4": {
        "DEEPAKNTR.NS":"Deepak Nitrite","DEEPIND.NS":"Deepak Spinners","DELTACORP.NS":"Delta Corp","DENDRO.NS":"Dendro Technologies",
        "DENORA.NS":"De Nora India","DENZYME.NS":"Dezyne E-Commerce","DHANBANK.NS":"Dhanalakshmi Bank","DHANUKA.NS":"Dhanuka Agritech",
        "DHARAMSI.NS":"Dharamsi Morarji","DHAMPURSUG.NS":"Dhampur Sugar","DHANVARSHA.NS":"Dhanvarsha Finvest","DHUNINV.NS":"Dhunseri Investments",
        "DIACABS.NS":"Diamond Cables","DIAMINESQ.NS":"Diamines Chemicals","DIGJAM.NS":"Digjamlimited","DIGISPICE.NS":"DiGiSPICE Technologies",
        "DIGJAMLMTD.NS":"Digjamlimited","DION.NS":"Dion Global Solutions","DISHMAN.NS":"Dishman Carbogen","DIVGIITTS.NS":"Divgi TorqTransfer",
        "DISHTV.NS":"Dish TV India","DIVISLAB.NS":"Divi's Laboratories","DIXON.NS":"Dixon Technologies","DLF.NS":"DLF"
    },
    "IT Software Services 1": {
        "DLINKINDIA.NS":"D-Link India","DMART.NS":"Avenue Supermarts","DMCC.NS":"DMCC Speciality","DOLLAR.NS":"Dollar Industries",
        "DOLAT.NS":"Dolat Investments","DONEAR.NS":"Donear Industries","DOUBLECON.NS":"Double Con","DREDGECORP.NS":"Dredging Corporation",
        "DRREDDY.NS":"Dr Reddy's Labs","DUCON.NS":"Ducon Infratechnologies","DUCOL.NS":"Ducol Organics","DUMMETT.NS":"Dummett Coote",
        "DWARKESH.NS":"Dwarkesh Sugar","DYNAMATECH.NS":"Dynamatic Technologies","DYNAMIND.NS":"Dynamatic Technologies","EASEMYTRIP.NS":"EaseMyTrip",
        "EASTSILK.NS":"Eastern Silk","EASUNREYRL.NS":"Easun Reyrolle","EBBCO.NS":"EbbCo Ventures","ECLFINANCE.NS":"Edelweiss Capital",
        "ECLERX.NS":"eClerx Services","ECOBOARD.NS":"Eco Board","EDELWEISS.NS":"Edelweiss Financial","EDUCOMP.NS":"Educomp Solutions"
    },
    "IT Software Services 2": {
        "EICHERMOT.NS":"Eicher Motors","EIDPARRY.NS":"EID Parry","EIFFL.NS":"Euro India Fresh Foods","EIHAHOTELS.NS":"EIH Associated Hotels",
        "EIHOTEL.NS":"EIH Ltd","EIMCOELECO.NS":"Eimco Elecon","EKENNIS.NS":"Ekennis Software","ELECTROCAST.NS":"Electrocast Sales",
        "ELECON.NS":"Elecon Engineering","ELECTHERM.NS":"Electrotherm India","ELGIRUBCO.NS":"Elgi Rubber","ELGIEQUIP.NS":"Elgi Equipments",
        "ELIN.NS":"Elin Electronics","EMAMILTD.NS":"Emami","EMAMIPAP.NS":"Emami Paper","EMAMIREAL.NS":"Emami Realty",
        "EMIRATE.NS":"Emirate Securities","EMMBI.NS":"Emmbi Industries","EMSLIMITED.NS":"EMS Ltd","ENIL.NS":"Entertainment Network",
        "EPACK.NS":"Epack Durables","EQUITAS.NS":"Equitas Holdings","EQUIPPP.NS":"Equippp Social","ERIS.NS":"Eris Lifesciences"
    },
    "IT Software Services 3": {
        "EROSMEDIA.NS":"Eros International","ESABINDIA.NS":"ESAB India","ESCORTS.NS":"Escorts Kubota","ESSARSHPNG.NS":"Essar Shipping",
        "ESTER.NS":"Ester Industries","ETECHNO.NS":"Electrotherm Technologies","EUROCERA.NS":"Euro Ceramics","EUROTEXIND.NS":"Eurotex Industries",
        "EVEREADY.NS":"Eveready Industries","EVERESTIND.NS":"Everest Industries","EXCEL.NS":"Excel Crop Care","EXCELINDUS.NS":"Excel Industries",
        "EXIDEIND.NS":"Exide Industries","EXPLEOSOL.NS":"Expleo Solutions","FACT.NS":"Fertilizers And Chemicals","FAGBEARING.NS":"Schaeffler India",
        "FAIRCHEM.NS":"Fairchem Speciality","FAZE3.NS":"Faze Three","FCL.NS":"Fineotex Chemical","FEDERALBNK.NS":"Federal Bank",
        "FEL.NS":"Future Enterprises","FELDVR.NS":"Future Enterprises DVR","FENTURA.NS":"Fentura Financial","FCSSOFT.NS":"FCS Software"
    },
    "IT Software Services 4": {
        "FIBERWEB.NS":"Fiberweb India","FIEMIND.NS":"Fiem Industries","FILATEX.NS":"Filatex India","FINCABLES.NS":"Finolex Cables",
        "FINOPB.NS":"Fino Payments","FINPIPE.NS":"Finolex Industries","FINEORG.NS":"Fine Organic","FINKURVE.NS":"Finkurve Financial",
        "FINOL.NS":"Finolex Industries","FIRSTCRY.NS":"FirstCry Baby","FIRSTSOUR.NS":"Firstsource Solutions","FIVESTAR.NS":"Five Star Business",
        "FLFL.NS":"Future Lifestyle","FLIP.NS":"Flip Media","FLUOROCHEM.NS":"Gujarat Fluorochemicals","FOCUSLIGHT.NS":"Focus Lighting",
        "FOMENTO.NS":"Fomento Resorts","FOODSIN.NS":"Foods & Inns","FORCE.NS":"Force Motors","FORCEMOT.NS":"Force Motors",
        "FORTIS.NS":"Fortis Healthcare","FOSECOIND.NS":"Foseco India","FRETAIL.NS":"Future Retail","FRIEDBERG.NS":"Friedberg Direct"
    },
    "Infrastructure Real Estate 1": {
        "FSC.NS":"Future Supply Chain","FSL.NS":"Firstsource Solutions","GABRIEL.NS":"Gabriel India","GAEL.NS":"Gujarat Ambuja Exports",
        "GAIL.NS":"GAIL India","GALAXYSURF.NS":"Galaxy Surfactants","GALLANTT.NS":"Gallantt Ispat","GANDHAR.NS":"Gandhar Oil Refinery",
        "GANDHITUBE.NS":"Gandhi Special Tubes","GANESHHOUC.NS":"Ganesh Housing","GANECOS.NS":"Ganesha Ecosphere","GANESHBE.NS":"Ganesh Benzoplast",
        "GARFIBRES.NS":"Garware Technical","GATI.NS":"Gati Ltd","GATECABLE.NS":"Gate Way Distriparks","GATEWAY.NS":"Gateway Distriparks",
        "GAYAHWS.NS":"Gayatri Highways","GDL.NS":"Gateway Distriparks","GENCON.NS":"Generic Pharma","GENSOL.NS":"Gensol Engineering",
        "GEOJITFSL.NS":"Geojit Financial","GEPIL.NS":"GE Power India","GESHIP.NS":"Great Eastern Shipping","GHCL.NS":"GHCL Ltd"
    },
    "Infrastructure Real Estate 2": {
        "GHCLTEXTIL.NS":"GHCL Textiles","GICHSGFIN.NS":"GIC Housing Finance","GICRE.NS":"GIC Re","GILLANDERS.NS":"Gillanders Arbuthnot",
        "GILLETTE.NS":"Gillette India","GINNIFILA.NS":"Ginni Filaments","GIPCL.NS":"Gujarat Industries","GISOLUTION.NS":"GI Engineering Solutions",
        "GITANJALI.NS":"Gitanjali Gems","GKWLIMITED.NS":"GKW Ltd","GLAND.NS":"Gland Pharma","GLAXO.NS":"GlaxoSmithKline Pharma",
        "GLFL.NS":"Gujarat Lease Financing","GLENMARK.NS":"Glenmark Pharma","GLOBALPET.NS":"Global Pet Industries","GLOBOFFS.NS":"Global Offshore",
        "GLOBALVECT.NS":"Global Vectra","GLOBUSSPR.NS":"Globus Spirits","GLORY.NS":"Glory Polyfilms","GMBREW.NS":"GM Breweries",
        "GMDCLTD.NS":"Gujarat Mineral","GMMPFAUDLR.NS":"GMM Pfaudler","GMRINFRA.NS":"GMR Infrastructure","GNA.NS":"GNA Axles"
    },
    "Infrastructure Real Estate 3": {
        "GNFC.NS":"GNFC","GOACARBON.NS":"Goa Carbon","GODFRYPHLP.NS":"Godfrey Phillips","GODREJAGRO.NS":"Godrej Agrovet",
        "GODREJCP.NS":"Godrej Consumer","GODREJIND.NS":"Godrej Industries","GODREJPROP.NS":"Godrej Properties","GOENKA.NS":"Goenka Business",
        "GOKEX.NS":"Gokaldas Exports","GOKUL.NS":"Gokul Refoils","GOKULMECH.NS":"Gokul Agro","GOLDBEES.NS":"Gold BeES",
        "GOLDTECH.NS":"Goldstone Technologies","GOODLUCK.NS":"Goodluck India","GOODYEAR.NS":"Goodyear India","GPIL.NS":"Godawari Power",
        "GPTINFRA.NS":"GPT Infraprojects","GPPL.NS":"Gujarat Pipavav","GRABALALK.NS":"Grasim Industries","GRAUWEIL.NS":"Grauer Weil India",
        "GRAVITA.NS":"Gravita India","GREAVESCOT.NS":"Greaves Cotton","GREENLAM.NS":"Greenlam Industries","GREENPLY.NS":"Greenply Industries"
    },
    "Infrastructure Real Estate 4": {
        "GREENPOWER.NS":"Greenpower Motor","GRINDWELL.NS":"Grindwell Norton","GRMOVER.NS":"GRM Overseas","GRPLTD.NS":"GRP Ltd",
        "GRSE.NS":"Garden Reach Shipbuilders","GRUH.NS":"Gruh Finance","GSFC.NS":"GSFC","GSPL.NS":"Gujarat State Petronet",
        "GTL.NS":"GTL Ltd","GTLINFRA.NS":"GTL Infrastructure","GTMLIMITED.NS":"GTM Ltd","GTPL.NS":"GTPL Hathway",
        "GUFICBIO.NS":"Gufic Biosciences","GUJALKALI.NS":"Gujarat Alkalies","GUJAPOLLO.NS":"Gujarat Apollo","GUJGASLTD.NS":"Gujarat Gas",
        "GUJNREDVR.NS":"Gujarat NRE Coke","GUJRAFFIA.NS":"Gujarat Raffia","GULFOILLUB.NS":"Gulf Oil Lubricants","GULFPETRO.NS":"GP Petroleums",
        "GVKPIL.NS":"GVK Power","GVPTECH.NS":"GVP Infotech","HALONIX.NS":"Halonix Technologies","HAL.NS":"Hindustan Aeronautics"
    },
    "Energy Utilities 1": {
        "HAMSUNDAR.NS":"Hamsund Enterprise","HAPPSTMNDS.NS":"Happiest Minds","HARDWYN.NS":"Hardwyn India","HARRMALAYA.NS":"Harrisons Malayalam",
        "HARSHA.NS":"Harsha Engineers","HATHWAY.NS":"Hathway Cable","HATSUN.NS":"Hatsun Agro","HAVELLS.NS":"Havells India",
        "HBLPOWER.NS":"HBL Power Systems","HBSL.NS":"HB Stockholdings","HCC.NS":"Hindustan Construction","HCLTECH.NS":"HCL Technologies",
        "HEG.NS":"HEG Ltd","HEIDELBERG.NS":"HeidelbergCement India","HELIOS.NS":"Helios Matheson","HERANBA.NS":"Heranba Industries",
        "HERCULES.NS":"Hercules Hoists","HERITGFOOD.NS":"Heritage Foods","HEROMOTOCO.NS":"Hero MotoCorp","HESTERBIO.NS":"Hester Biosciences",
        "HEUBACHIND.NS":"Heubach Colorants","HEXATRADEX.NS":"Hexa Tradex","HEXAWARE.NS":"Hexaware Technologies","HFCL.NS":"HFCL Ltd"
    },
    "Energy Utilities 2": {
        "HGS.NS":"Hinduja Global","HIKAL.NS":"Hikal Ltd","HIL.NS":"HIL Ltd","HILTON.NS":"Hilton Metal",
        "HIMATSEIDE.NS":"Himatsingka Seide","HINDCOMPOS.NS":"Hindustan Composites","HINDCOPPER.NS":"Hindustan Copper","HINDDORROL.NS":"Hinddorrol",
        "HINDMOTORS.NS":"Hindustan Motors","HINDNATGLS.NS":"Hindon Natural","HINDOILEXP.NS":"Hindustan Oil Exploration","HINDPETRO.NS":"Hindustan Petroleum",
        "HINDUNILVR.NS":"Hindustan Unilever","HINDWAREAP.NS":"Hindware Appliances","HINDZINC.NS":"Hindustan Zinc","HIRECT.NS":"Hind Rectifiers",
        "HITECH.NS":"Hitech Corporation","HITECHCORP.NS":"Hitech Corporation","HITECHGEAR.NS":"Hitachi Energy","HLEGLAS.NS":"HLE Glascoat",
        "HMT.NS":"HMT Ltd","HMVL.NS":"Hindustan Media","HNDFDS.NS":"Hindustan Foods","HOMEFIRST.NS":"Home First Finance"
    },
    "Energy Utilities 3": {
        "HONAUT.NS":"Honeywell Automation","HONDAPOWER.NS":"Honda Power","HOTELRUGBY.NS":"Hotel Rugby","HOVS.NS":"HOV Services",
        "HPAL.NS":"HP Adhesives","HPL.NS":"HPL Electric","HSCL.NS":"Himadri Speciality","HTMEDIA.NS":"HT Media",
        "HUDCO.NS":"HUDCO","HUHTAMAKI.NS":"Huhtamaki India","ICICIBANK.NS":"ICICI Bank","ICICIGI.NS":"ICICI Lombard",
        "ICICIPRULI.NS":"ICICI Prudential","ICIL.NS":"Indo Count","ICRA.NS":"ICRA Ltd","IDBI.NS":"IDBI Bank",
        "IDEA.NS":"Vodafone Idea","IDFC.NS":"IDFC Ltd","IDFCFIRSTB.NS":"IDFC First Bank","IEX.NS":"Indian Energy Exchange",
        "IFBAGRO.NS":"IFB Agro","IFBIND.NS":"IFB Industries","IFCI.NS":"IFCI Ltd","IFGLEXPOR.NS":"IFGL Refractories"
    },
    "Energy Utilities 4": {
        "IGARASHI.NS":"Igarashi Motors","IGL.NS":"Indraprastha Gas","IGPL.NS":"IG Petrochemicals","IITL.NS":"Industrial Investment",
        "IIFL.NS":"IIFL Finance","IIFLSEC.NS":"IIFL Securities","IIFLWAM.NS":"IIFL Wealth","IMAGICAA.NS":"Imagicaa World",
        "IMFA.NS":"Indian Metals","IMPAL.NS":"India Cements","INANI.NS":"Inani Marbles","INCA.NS":"India Nippon",
        "INDBANK.NS":"Indbank Merchant","INDHOTEL.NS":"Indian Hotels","INDIANB.NS":"Indian Bank","INDIANCARD.NS":"Indian Card",
        "INDIANHUME.NS":"Indian Hume Pipe","INDIAMART.NS":"IndiaMART","INDIASHLTR.NS":"India Shelter","INDIGO.NS":"InterGlobe Aviation",
        "INDIGOPNTS.NS":"Indigo Paints","INDITNX.NS":"India Nivesh","INDNIPPON.NS":"India Nippon","INDOAMIN.NS":"Indo Amines"
    },
    "Banking Financial Services 1": {
        "INDOBORAX.NS":"Indo Borax","INDOCO.NS":"Indoco Remedies","INDOCOUNT.NS":"Indo Count","INDOFIL.NS":"Indofil Industries",
        "INDOKEM.NS":"Indokem Ltd","INDOMETAL.NS":"Indo Metal","INDORAMA.NS":"Indo Rama Synthetics","INDOSOLAR.NS":"Indosolar",
        "INDOSTAR.NS":"IndoStar Capital","INDOTECH.NS":"Indo Tech","INDOTHAI.NS":"Indo Thai Securities","INDOWIND.NS":"Indowind Energy",
        "INDRAMEDCO.NS":"Indraprastha Medical","INDSWFTLAB.NS":"Ind-Swift Laboratories","INDSWFTLTD.NS":"Ind-Swift Ltd","INDTERRAIN.NS":"Indian Terrain",
        "INDUSINDBK.NS":"IndusInd Bank","INDUSTOWER.NS":"Indus Towers","INEOSSTYRO.NS":"INEOS Styrolution","INFOMEDIA.NS":"Infomedia Press",
        "INFY.NS":"Infosys","INGERRAND.NS":"Ingersoll Rand","INNOVACAP.NS":"Innovatus Capital","INOXGREEN.NS":"Inox Green"
    },
    "Banking Financial Services 2": {
        "INOXLEISUR.NS":"Inox Leisure","INOXWIND.NS":"Inox Wind","INSECTICID.NS":"Insecticides India","INTELLECT.NS":"Intellect Design",
        "INTENTECH.NS":"Intense Technologies","INTLCONV.NS":"International Conveyors","IOB.NS":"Indian Overseas Bank","IOC.NS":"Indian Oil",
        "IOLCP.NS":"IOL Chemicals","IPAPPM.NS":"Intrasoft Technologies","IPCALAB.NS":"IPCA Laboratories","IPL.NS":"India Pesticides",
        "IRB.NS":"IRB Infrastructure","IRCON.NS":"IRCON International","IRCTC.NS":"IRCTC","IRFC.NS":"IRFC",
        "IRISDOREME.NS":"Iris Clothings","IRISENERGY.NS":"Iris Energy","ISEC.NS":"ICICI Securities","ISFT.NS":"Intrasoft Technologies",
        "ISMTLTD.NS":"ISMT Ltd","ITC.NS":"ITC Ltd","ITDCEM.NS":"ITD Cementation","ITELGREEN.NS":"ITEL Greentech"
    },
    "Banking Financial Services 3": {
        "ITI.NS":"ITI Ltd","ITNL.NS":"IL&FS Transportation","IVRCL.NS":"IVRCL Ltd","IVP.NS":"IVP Ltd",
        "IWEL.NS":"Innotech Solutions","IZMO.NS":"IZMO Ltd","JAGRAN.NS":"Jagran Prakashan","JAGSNPHARM.NS":"Jagsonpal Pharma",
        "JAIBALAJI.NS":"Jai Balaji Industries","JAICORPLTD.NS":"Jaicorp Ltd","JAIHINDPRO.NS":"Jaihind Projects","JAIPURKURT.NS":"Nandani Creation",
        "JAMNAAUTO.NS":"Jamna Auto","JAYSREETEA.NS":"Jayshree Tea","JBCHEPHARM.NS":"JB Chemicals","JBFIND.NS":"JBF Industries",
        "JBMA.NS":"JBM Auto","JCHAC.NS":"Johnson Controls","JETAIRWAYS.NS":"Jet Airways","JETFREIGHT.NS":"Jet Freight Logistics",
        "JETINFRA.NS":"Jet Infrastructure","JFLLIFE.NS":"JFL Life Sciences","JIKIND.NS":"JIK Industries","JINDALPHOT.NS":"Jindal Photo"
    },
    "Banking Financial Services 4": {
        "JINDALPOLY.NS":"Jindal Poly Films","JINDALSAWNS":"Jindal Saw","JINDALSTEL.NS":"Jindal Steel","JINDWORLD.NS":"Jindal Worldwide",
        "JISLDVREQS.NS":"Jainam Share","JISLJALEQS.NS":"Jainam Jalaram","JITFINFRA.NS":"JITF Infralogistics","JKCEMENT.NS":"JK Cement",
        "JKLAKSHMI.NS":"JK Lakshmi Cement","JKPAPER.NS":"JK Paper","JKTYRE.NS":"JK Tyre","JMA.NS":"Jullundur Motor",
        "JMFINANCIL.NS":"JM Financial","JMTAUTOLTD.NS":"JMT Auto","JOCIL.NS":"Jocil Ltd","JONENG.NS":"Jones Engineering",
        "JPOLYINVST.NS":"Jindal Poly Investment","JSL.NS":"Jindal Stainless","JSLHISAR.NS":"Jindal Stainless Hisar","JSWENERGY.NS":"JSW Energy",
        "JSWHL.NS":"JSW Holdings","JSWISPL.NS":"JSW Ispat","JSWSTEEL.NS":"JSW Steel","JTEKTINDIA.NS":"JTEKT India"
    },
    "Food Beverages Agriculture 1": {
        "JTLIND.NS":"JTL Industries","JUBLFOOD.NS":"Jubilant FoodWorks","JUBLINDS.NS":"Jubilant Industries","JUBLPHARMA.NS":"Jubilant Pharma",
        "JUGGILAL.NS":"Juggilal Kamlapat","JUMBOAG.NS":"Jumbo Bag","JUMPNET.NS":"Jumpnet Technologies","JUSTDIAL.NS":"Just Dial",
        "JVLAGRO.NS":"JVL Agro","JYOTHYLAB.NS":"Jyothy Labs","JYOTISTRUC.NS":"Jyoti Structures","KABRAEXTRU.NS":"Kabra Extrusion",
        "KAJARIACER.NS":"Kajaria Ceramics","KAKATCEM.NS":"Kakatiya Cement","KALPATPOWR.NS":"Kalpataru Power","KALYANI.NS":"Kalyani Forge",
        "KALYANKJIL.NS":"Kalyan Jewellers","KAMDHENU.NS":"Kamdhenu Ltd","KAMOPAINTS.NS":"Kamdhenu Paints","KANANIIND.NS":"Kanani Industries",
        "KANORICHEM.NS":"Kanoria Chemicals","KANSAINER.NS":"Kansai Nerolac","KANPRPLA.NS":"Kanchenjunga Tea","KARDA.NS":"Karda Constructions"
    },
    "Food Beverages Agriculture 2": {
        "KARMAENG.NS":"Karma Energy","KARNIMATA.NS":"Karni Industries","KARNINVEST.NS":"Karni Investment","KARURVYSYA.NS":"Karur Vysya Bank",
        "KAUSHALYA.NS":"Kausalya Infrastructure","KAVVERITEL.NS":"Kavveri Telecom","KAYPITFIN.NS":"Kaypee Financing","KAYCEEI.NS":"Kayceei Industries",
        "KCP.NS":"KCP Ltd","KCPSUGIND.NS":"KCP Sugar","KDIL.NS":"Karnimata Data","KEI.NS":"KEI Industries",
        "KELLTONTEC.NS":"Kellton Tech","KERNEX.NS":"Kernex Microsystems","KESARWIRES.NS":"Kesar Wires","KEWAUNEE.NS":"Kewaunee Scientific",
        "KEYFINSERV.NS":"Keynote Financial","KEYTONE.NS":"Keytone Leasing","KFINTECH.NS":"KFin Technologies","KHANDSE.NS":"Khandwala Securities",
        "KHAIPULSE.NS":"Khaitanpulse","KICL.NS":"Kalyani Investment","KILITCH.NS":"Kilitch Drugs","KIMBERLY.NS":"Kimberly Clark"
    },
    "Food Beverages Agriculture 3": {
        "KINGFA.NS":"Kingfa Science","KIRIINDUS.NS":"Kiri Industries","KIRLOSBROS.NS":"Kirloskar Brothers","KIRLOSENG.NS":"Kirloskar Oil",
        "KIRLOSIND.NS":"Kirloskar Industries","KITEX.NS":"Kitex Garments","KKCL.NS":"Kewal Kiran Clothing","KKC.NS":"KKR & Co",
        "KMSUGAR.NS":"KM Sugar Mills","KNAGRI.NS":"KN Agri Resources","KNRCON.NS":"KNR Constructions","KODYTECH.NS":"Kody Technolab",
        "KOKUYOCMLN.NS":"Kokuyo Camlin","KOLTEPATIL.NS":"Kolte-Patil","KOPRAN.NS":"Kopran Ltd","KOSMOTEC.NS":"Kosmo e-Technology",
        "KOTARISUG.NS":"Kothari Sugars","KPITTECH.NS":"KPIT Technologies","KPIGREEN.NS":"KPI Green Energy","KPR.NS":"KPR Mill",
        "KPRMILL.NS":"KPR Mill","KRBL.NS":"KRBL Ltd","KREBSBIO.NS":"Krebs Biochemicals","KRIINFRA.NS":"K Raheja"
    },
    "Food Beverages Agriculture 4": {
        "KRIDHANINF.NS":"Kridhan Infra","KRISHANA.NS":"Krishana Phoschem","KRITI.NS":"Kriti Industries","KRITIKA.NS":"Kritika Wires",
        "KRITINUT.NS":"Kriti Nutrients","KRONS.NS":"Kronox Lab Sciences","KRSNAA.NS":"Krsnaa Diagnostics","KSB.NS":"KSB Ltd",
        "KSE.NS":"KSS Ltd","KSK.NS":"KSK Energy Ventures","KTKBANK.NS":"Karnataka Bank","KUBOTA.NS":"Escorts Kubota",
        "KUMARASWA.NS":"Kumar Swamy Construction","KUMARKS.NS":"Kumar Swamy","KUMBHAT.NS":"Kumbhat Financial","KUNDANCARE.NS":"Kundan Care",
        "KUPRIYA.NS":"Kupriya Industries","KUSTODIAN.NS":"Kustodian Securities","KWALITY.NS":"Kwality Ltd","KWALIT.NS":"Kwalitex Industries",
        "L&TFH.NS":"L&T Finance Holdings","L&TFHIN.NS":"L&T Finance","L&T.NS":"Larsen & Toubro","LA.NS":"Laurus Labs"
    },
    "Retail Media Entertainment 1": {
        "LAKPRE.NS":"Lakshmi Precision","LAKSHMIEFL.NS":"Lakshmi Energy","LALPATHLAB.NS":"Dr Lal PathLabs","LAMBODHARA.NS":"Lambodhara Textiles",
        "LANCER.NS":"Lancer Container","LANDMARK.NS":"Landmark Property","LAOPALA.NS":"La Opala RG","LASA.NS":"Lasa Supergenerics",
        "LATENTVIEW.NS":"LatentView Analytics","LAURUSLABS.NS":"Laurus Labs","LAXMIMACH.NS":"Lakshmi Machine","LCCINFOTEC.NS":"LCC Infotech",
        "LCC.NS":"LCC Infotech","LEMONTREE.NS":"Lemon Tree Hotels","LEXUS.NS":"Lexus Granito","LFIC.NS":"Lakshmi Finance",
        "LG.NS":"LG Balakrishnan","LGBBROSLTD.NS":"LG Balakrishnan","LGBFORGE.NS":"LG Balakrishnan Forge","LGHL.NS":"LG Balakrishnan",
        "LIBAS.NS":"Libas Designs","LIBERTSHOE.NS":"Liberty Shoes","LICNETFN50.NS":"LIC MF Nifty 50","LICHSGFIN.NS":"LIC Housing Finance"
    },
    "Retail Media Entertainment 2": {
        "LINCPEN.NS":"Lincoln Pharmaceuticals","LINDEINDIA.NS":"Linde India","LINKINTIME.NS":"Link Intime","LKINVESTING.NS":"LKP Finance",
        "LLOYDSME.NS":"Lloyds Metals","LLOYDS.NS":"Lloyds Enterprises","LODHA.NS":"Lodha","LOKESHMACH.NS":"Lokesh Machines",
        "LOTUSEYE.NS":"Lotus Eye Care","LPDC.NS":"Landmark Property","LT.NS":"Larsen Toubro","LTFOODS.NS":"LT Foods",
        "LTIM.NS":"LTIMindtree","LUMAXIND.NS":"Lumax Industries","LUMAXTECH.NS":"Lumax Auto Tech","LUPIN.NS":"Lupin"
    }
}

INDUSTRY_BENCHMARKS = {
    'Technology': {'pe': 30, 'ev_ebitda': 18},'Financial Services': {'pe': 18, 'ev_ebitda': 12},'Consumer Cyclical': {'pe': 35, 'ev_ebitda': 18},
    'Consumer Defensive': {'pe': 40, 'ev_ebitda': 20},'Healthcare': {'pe': 32, 'ev_ebitda': 18},'Industrials': {'pe': 28, 'ev_ebitda': 16},
    'Energy': {'pe': 20, 'ev_ebitda': 12},'Basic Materials': {'pe': 22, 'ev_ebitda': 14},'Real Estate': {'pe': 30, 'ev_ebitda': 22},'Default': {'pe': 24, 'ev_ebitda': 16}
}

def retry_with_backoff(retries=5, backoff_in_seconds=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        raise
                    time.sleep(backoff_in_seconds * 2 ** x)
                    x += 1
        return wrapper
    return decorator

@st.cache_data(ttl=10800)
@retry_with_backoff(retries=5, backoff_in_seconds=3)
def fetch_stock_data(ticker):
    try:
        time.sleep(1.5)
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or len(info) < 5:
            return None, "Unable to fetch data"
        return info, None
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "rate" in error_msg.lower() or "limit" in error_msg.lower():
            return None, "RATE_LIMIT"
        return None, str(e)[:100]

def calculate_valuations(info):
    try:
        price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
        trailing_pe = info.get('trailingPE', 0)
        forward_pe = info.get('forwardPE', 0)
        trailing_eps = info.get('trailingEps', 0)
        enterprise_value = info.get('enterpriseValue', 0)
        ebitda = info.get('ebitda', 0)
        market_cap = info.get('marketCap', 0)
        shares = info.get('sharesOutstanding', 1)
        sector = info.get('sector', 'Default')
        benchmark = INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS['Default'])
        industry_pe = benchmark['pe']
        industry_ev_ebitda = benchmark['ev_ebitda']
        historical_pe = trailing_pe * 0.85 if trailing_pe and trailing_pe > 0 else industry_pe
        blended_pe = (industry_pe + historical_pe) / 2
        fair_value_pe = trailing_eps * blended_pe if trailing_eps else None
        upside_pe = ((fair_value_pe - price) / price * 100) if fair_value_pe and price else None
        current_ev_ebitda = enterprise_value / ebitda if ebitda and ebitda > 0 else None
        target_ev_ebitda = (industry_ev_ebitda + current_ev_ebitda * 0.85) / 2 if current_ev_ebitda and 0 < current_ev_ebitda < 50 else industry_ev_ebitda
        if ebitda and ebitda > 0:
            fair_ev = ebitda * target_ev_ebitda
            net_debt = (info.get('totalDebt', 0) or 0) - (info.get('totalCash', 0) or 0)
            fair_mcap = fair_ev - net_debt
            fair_value_ev = fair_mcap / shares if shares else None
            upside_ev = ((fair_value_ev - price) / price * 100) if fair_value_ev and price else None
        else:
            fair_value_ev = None
            upside_ev = None
        return {
            'price': price, 'trailing_pe': trailing_pe, 'forward_pe': forward_pe,'trailing_eps': trailing_eps, 'industry_pe': industry_pe,
            'fair_value_pe': fair_value_pe, 'upside_pe': upside_pe,'enterprise_value': enterprise_value, 'ebitda': ebitda,
            'market_cap': market_cap, 'current_ev_ebitda': current_ev_ebitda,'industry_ev_ebitda': industry_ev_ebitda,
            'fair_value_ev': fair_value_ev, 'upside_ev': upside_ev
        }
    except:
        return None

def create_gauge_chart(upside_pe, upside_ev):
    fig = make_subplots(rows=1, cols=2,specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],subplot_titles=("PE Multiple", "EV/EBITDA"))
    fig.add_trace(go.Indicator(mode="gauge+number",value=upside_pe,number={'suffix': "%", 'font': {'size': 40}},
        gauge={'axis': {'range': [-50, 50]},'bar': {'color': "#43e97b"},'steps': [{'range': [-50, 0], 'color': '#ffebee'},{'range': [0, 50], 'color': '#e8f5e9'}],
        'threshold': {'line': {'color': "red", 'width': 4}, 'value': 0}}), row=1, col=1)
    fig.add_trace(go.Indicator(mode="gauge+number",value=upside_ev,number={'suffix': "%", 'font': {'size': 40}},
        gauge={'axis': {'range': [-50, 50]},'bar': {'color': "#fa709a"},'steps': [{'range': [-50, 0], 'color': '#ffebee'},{'range': [0, 50], 'color': '#e8f5e9'}],
        'threshold': {'line': {'color': "red", 'width': 4}, 'value': 0}}), row=1, col=2)
    fig.update_layout(height=400)
    return fig

def create_bar_chart(vals):
    categories, current, fair, colors_fair = [], [], [], []
    if vals['fair_value_pe']:
        categories.append('PE Multiple')
        current.append(vals['price'])
        fair.append(vals['fair_value_pe'])
        colors_fair.append('#00C853' if vals['fair_value_pe'] > vals['price'] else '#e74c3c')
    if vals['fair_value_ev']:
        categories.append('EV/EBITDA')
        current.append(vals['price'])
        fair.append(vals['fair_value_ev'])
        colors_fair.append('#00C853' if vals['fair_value_ev'] > vals['price'] else '#e74c3c')
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Current', x=categories, y=current, marker_color='#3498db',text=[f'Rs {p:.2f}' for p in current], textposition='outside'))
    fig.add_trace(go.Bar(name='Fair Value', x=categories, y=fair, marker_color=colors_fair,text=[f'Rs {p:.2f}' for p in fair], textposition='outside'))
    fig.update_layout(barmode='group', height=500, template='plotly_white')
    return fig

def create_pdf_report(company, ticker, sector, vals):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#43e97b'), alignment=TA_CENTER)
    story = []
    story.append(Paragraph("NYZTrade Smallcap Report", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>{company}</b>", styles['Heading2']))
    story.append(Paragraph(f"Ticker: {ticker} | Sector: {sector}", styles['Normal']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 30))
    ups = [v for v in [vals['upside_pe'], vals['upside_ev']] if v is not None]
    avg_up = np.mean(ups) if ups else 0
    fairs = [v for v in [vals['fair_value_pe'], vals['fair_value_ev']] if v is not None]
    avg_fair = np.mean(fairs) if fairs else vals['price']
    fair_data = [['Metric', 'Value'],['Fair Value', f"Rs {avg_fair:.2f}"],['Current Price', f"Rs {vals['price']:.2f}"],['Upside', f"{avg_up:+.2f}%"]]
    fair_table = Table(fair_data, colWidths=[3*inch, 2*inch])
    fair_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#43e97b')),('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    story.append(fair_table)
    story.append(Spacer(1, 20))
    metrics_data = [['Metric', 'Value'],['Current Price', f"Rs {vals['price']:.2f}"],['PE Ratio', f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else 'N/A'],
        ['EPS', f"Rs {vals['trailing_eps']:.2f}" if vals['trailing_eps'] else 'N/A'],['Market Cap', f"Rs {vals['market_cap']/10000000:.2f} Cr"]]
    metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
    metrics_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    story.append(metrics_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("DISCLAIMER: Educational content only, not financial advice.", styles['Normal']))
    doc.build(story)
    buffer.seek(0)
    return buffer

st.markdown('<div class="main-header"><h1>SMALLCAP VALUATION</h1><p>795+ High Growth Stocks | Professional Analysis</p></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.info("💡 **3-Hour Caching** - Lightning fast!")
with col2:
    st.success("📊 **795+ Stocks** - Comprehensive coverage")
with col3:
    st.warning("⚡ **Smart Rate Limits** - Optimized")

if st.sidebar.button("Logout", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.sidebar.header("Stock Selection")

all_stocks = {}
for cat, stocks in SMALLCAP_STOCKS.items():
    all_stocks.update(stocks)

st.sidebar.success(f"Total: {len(all_stocks)} stocks")

category = st.sidebar.selectbox("Category", ["All Stocks"] + list(SMALLCAP_STOCKS.keys()))
search = st.sidebar.text_input("Search", placeholder="Company or ticker")

if search:
    filtered = {t: n for t, n in all_stocks.items() if search.upper() in t or search.upper() in n.upper()}
elif category == "All Stocks":
    filtered = all_stocks
else:
    filtered = SMALLCAP_STOCKS[category]

if filtered:
    options = [f"{n} ({t})" for t, n in filtered.items()]
    selected = st.sidebar.selectbox("Select Stock", options)
    ticker = selected.split("(")[1].strip(")")
else:
    ticker = None
    st.sidebar.warning("No stocks found")

custom = st.sidebar.text_input("Custom Ticker", placeholder="e.g., DIXON.NS")

with st.sidebar.expander("⚡ Rate Limit Guidelines"):
    st.markdown("""
    **Smart Caching System:**
    - Data cached for 3 hours
    - Reanalyzing same stock = Instant!
    - No API quota used on cached data
    
    **If Rate Limit Occurs:**
    1. Wait 3-5 minutes
    2. Try a different stock
    3. Cached stocks load instantly
    
    **Tip:** Analyze during off-peak hours (9 AM - 5 PM IST)
    """)

if st.sidebar.button("ANALYZE", use_container_width=True):
    st.session_state.analyze = custom.upper() if custom else ticker

if 'analyze' in st.session_state:
    t = st.session_state.analyze
    with st.spinner(f"Analyzing {t}..."):
        info, error = fetch_stock_data(t)
    
    if error:
        if error == "RATE_LIMIT":
            st.error("⏱️ RATE LIMIT REACHED")
            st.warning("""
            **Yahoo Finance API limit hit. Please:**
            
            1. ⏰ **Wait 3-5 minutes** and try again
            2. 🔄 **Try a different stock** (stocks analyzed in last 3 hours load instantly!)
            3. 📊 **Check cached stocks** - They don't use API quota
            4. 🕐 **Analyze during off-peak hours** for better experience
            
            **Why this happens:**
            - Free Yahoo Finance API: 2,000 requests/hour
            - Multiple users accessing simultaneously
            
            **Pro Tip:** Recently analyzed stocks are cached for 3 hours!
            """)
        else:
            st.error(f"Error: {error}")
        st.stop()
    
    if not info:
        st.error("Failed to fetch data")
        st.stop()
    
    vals = calculate_valuations(info)
    if not vals:
        st.error("Valuation failed")
        st.stop()
    
    company = info.get('longName', t)
    sector = info.get('sector', 'N/A')
    st.markdown(f"## {company}")
    st.markdown(f"**Sector:** {sector} | **Ticker:** {t}")
    ups = [v for v in [vals['upside_pe'], vals['upside_ev']] if v is not None]
    avg_up = np.mean(ups) if ups else 0
    fairs = [v for v in [vals['fair_value_pe'], vals['fair_value_ev']] if v is not None]
    avg_fair = np.mean(fairs) if fairs else vals['price']
    fair_html = f'<div class="fair-value-box"><h2>FAIR VALUE</h2><h1>Rs {avg_fair:.2f}</h1><p>Current: Rs {vals["price"]:.2f}</p><h3>Upside: {avg_up:+.2f}%</h3></div>'
    st.markdown(fair_html, unsafe_allow_html=True)
    pdf = create_pdf_report(company, t, sector, vals)
    st.download_button("Download PDF", data=pdf, file_name=f"NYZTrade_Smallcap_{t}_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Price", f"Rs {vals['price']:.2f}")
    with col2:
        st.metric("PE", f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else "N/A")
    with col3:
        st.metric("EPS", f"Rs {vals['trailing_eps']:.2f}" if vals['trailing_eps'] else "N/A")
    with col4:
        st.metric("MCap", f"Rs {vals['market_cap']/10000000:.0f} Cr")
    if avg_up > 30:
        rec_class, rec_text = "rec-strong-buy", "STRONG BUY"
    elif avg_up > 20:
        rec_class, rec_text = "rec-buy", "BUY"
    elif avg_up > 0:
        rec_class, rec_text = "rec-buy", "ACCUMULATE"
    elif avg_up > -15:
        rec_class, rec_text = "rec-hold", "HOLD"
    else:
        rec_class, rec_text = "rec-avoid", "AVOID"
    rec_html = f'<div class="{rec_class}">{rec_text}<br>Return: {avg_up:+.2f}%</div>'
    st.markdown(rec_html, unsafe_allow_html=True)
    st.markdown("---")
    if vals['upside_pe'] and vals['upside_ev']:
        st.subheader("Valuation Analysis")
        fig1 = create_gauge_chart(vals['upside_pe'], vals['upside_ev'])
        st.plotly_chart(fig1, use_container_width=True)
    fig2 = create_bar_chart(vals)
    st.plotly_chart(fig2, use_container_width=True)
    st.subheader("Financial Metrics")
    df = pd.DataFrame({
        'Metric': ['Current Price','PE Ratio','Industry PE','EPS','Market Cap','Enterprise Value','EBITDA'],
        'Value': [f"Rs {vals['price']:.2f}",f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else 'N/A',f"{vals['industry_pe']:.2f}x",
            f"Rs {vals['trailing_eps']:.2f}" if vals['trailing_eps'] else 'N/A',f"Rs {vals['market_cap']/10000000:.0f} Cr",
            f"Rs {vals['enterprise_value']/10000000:.0f} Cr",f"Rs {vals['ebitda']/10000000:.0f} Cr" if vals['ebitda'] else 'N/A']
    })
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Select a stock and click ANALYZE")
    col1, col2 = st.columns(2)
    with col1:
        st.success("**Features:** 795+ smallcap stocks, High growth potential, Real-time analysis, PDF reports")
    with col2:
        st.warning("**Tip:** Smallcaps are more volatile. Data cached for 3 hours for faster access!")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>NYZTrade Smallcap Platform | 795+ Stocks | Educational Tool</div>", unsafe_allow_html=True)
