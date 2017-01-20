# coding=utf-8

from PyPDF2 import PdfFileReader  # use PyPDF2 instead of pypdf
from lxml import etree
import re
from model import *
import sys
reload (sys)
import string
import json

sys.setdefaultencoding("utf8")

class Extractor:
    # all the dictionaries are shared by all the instances of the class
    court_conversion = {
        "environmental protection": "epa", "massachu": "mad", "puerto": "prd",
        "immigration appeals": "immigration appeals", "maine": "med", "hampshire": "nhd", "rhode": "rid",
        "energy regulatory": "ferc", "national labor": "nlrb", "tax court": "tax court",
        "benefits review": "benefits review", "surface": "stb",
        "securities and exchange": "sec", "bankruptcy appellate": "bankruptcy appellate", "northern new": "nynd",
        "southern new": "nysd", "vermont": "vtd", "connecticut": "ctd", "eastern new": "nyed", "western new": "nywd",
        "maryland": "mdd", "eastern north carolina": "nced", "middle north carolina": "ncmd",
        "western north carolina": "ncwd", "south carolina": "scd", "western virginia": "vawd",
        "eastern virginia": "vaed", "northern west virginia": "wvnd", "southern west virginia": "wvsd",
        "eastern louisiana": "laed", "middle louisiana": "lamd", "western louisiana": "lawd",
        "northern mississippi": "msnd", "southern mississippi": "mssd", "eastern texas": "txed",
        "northern texas": "txnd", "southern texas": "txsd", "western texas": "txwd", "eastern kentucky": "kyed",
        "western kentucky": "kywd", "eastern michigan": "mied", "western michigan": "miwd", "northern ohio": "ohnd",
        "southern ohio": "ohsd", "eastern tennessee": "tned", "middle tennessee": "tnmd",
        "western tennessee": "tnwd", "northern illinois": "ilnd", "central illinois": "ilcd",
        "southern illinois": "ilsd", "northern indiana": "innd", "southern indiana": "insd",
        "eastern wisconsin": "wied", "western wisconsin": "wiwd", "eastern arkansas": "ared",
        "western arkansas": "arwd", "northern iowa": "iand", "southern iowa": "iasd", "minnesota": "mnd",
        "eastern missouri": "moed", "western missouri": "mowd", "nebraska": "nbd", "north dakota": "ndd",
        "south dakota": "sdd",
        "columbia": "dcd",
        "alaska": "akd",
        # adding 9th circuit's appellate jurisdiction
        "arizona": "azd",
        "central california": "cacd", "eastern california": "caed", "northern california": "cand", "southern california": "casd",
        "hawaii": "hid",
        "idaho": "idd",
        "montana": "mtd",
        "nevada": "nvd",
        "oregon": "ord",
        "eastern washington": "waed", "western washington": "wawd",
        # adding 10th circuit's appellate jurisdiction
        "colorado": "cod",
        "kansas": "ksd",
        "new mexico": "nmd",
        "eastern oklahoma": "oked", "northern oklahoma": "oknd", "western oklahoma": "okwd",
        "utah": "utd",
        "wyoming":"wyd",
        # adding 11th circuit's appellate jurisdiction
        "middle alabama": "almd", "northern alabama": "alnd", "southern alabama": "alsd",
        "middle florida": "flmd", "northern florida": "flnd", "southern florida": "flsd",
        "middle georgia": "gamd", "northern georgia": "gand", "southern georgia": "gasd",        
    }

    circuit_judges = {
        # remember to check the judges
        "1st": ["Howard", "Torruella", "Lynch", "Thompson", "Kayatta", "Barron", "Selya", "Boudin", "Stahl", "Lipez"],
        "2nd": ["Katzmann", "Newman", "Kearse", "Winter", "Walker", "Jacobs", "Leval", "Calabresi", "Cabranes",
                "Straub", "Pooler", "Sack", "Parker", "Raggi", "Wesley", "Hall", "Livingston", "Lynch", "Chin",
                "Lohier", "Carney", "Droney", "RK", "DGJ", "JAC", "RSP", "RR", "PWH", "DAL", "DC", "RL", "SLC", "CFD", 
                "JON", "ALK", "RKW", "JMW", "PNL", "GC", "CJS", "RDS", "BDP", "RCW", "GEL"],

        "3rd": ["McKee", "Ambro", "Fuentes", "Smith", "Fisher", "Chagares", "Jordan", "Hardiman", "Greenaway",
                "Vanaskie", "Shwartz", "Krause", "Garth", "Sloviter", "Stapleton", "Greenberg", "Scirica", "Cowen",
                "Nygaard", "Roth", "Rendell", "Barry", "Van Antwerpen"],
        "4th": ["Traxler", "Wilkinson", "Niemeyer", "Motz", "King", "Gregory", "Shedd", "Duncan", "Agee", "Keenan",
                "Wynn", "Diaz", "Floyd", "Thacker", "Harris", "Hamilton", "Davis"],
        "5th": ["Stewart", "Reavley", "King", "Jolly", "Higginbotham", "Davis", "Jones", "Smith", u"Duhé", "Wiener",
                "Barksdale", "Benavides", "Dennis", "Clement", "Prado", "Owen", "Elrod", "Southwick", "Haynes",
                "Graves", "Higginson", "Costa"],
        "6th": ["Cole", "Keith", "Merritt", "Guy", "Boggs", "Norris", "Suhrheinrich", "Siler", "Batchelder",
                "Daughtrey", "Moore", "Clay", "Gilman", "Gibbons", "Rogers", "Sutton", "Cook", "McKeague",
                "Griffin", "Kethledge", "White", "Stranch", "Donald"],
        "7th": ["Wood", "Bauer", "Cudahy", "Posner", "Flaum", "Easterbrook", "Ripple", "Manion", "Kanne",
                "Rovner", "Williams", "Sykes", "Tinder", "Hamilton"],
        "8th": ["Riley", "Wollman", "Loken", "Murphy", "Smith", "Colloton", "Gruender", "Benton", "Shepherd",
                "Kelly", "Bright", "Bowman", "Beam", "Arnold", "Bye", "Melloy"],
        "dc": ["Roberts", "Garland", "Henderson", "Rogers", "Tatel", "Brown", "Griffith", "Kavanaugh",
               "Srinivasan", "Millett", "Pillard", "Wilkins", "Edwards", "Silberman", "Buckley",
               "Williams", "Ginsburg", "Sentelle", "Randolph", "Wald"],
        
#         adding 9th, 10th and 11th circuit_judges
#         there are two judges named Smith: Milan D. Smith and N. Randy Smith
        "9th": ["Thomas", "Reinhardt", "Kozinski", "O'Scannlain", "Graber", "McKeown", "Wardlaw", "Fletcher", "Gould",
                "Paez", "Berzon", "Tallman", "Rawlinson", "Clifton", "Bybee", "Callahan", "Bea", "D.Smith", "Ikuta",
                "Smith", "Murguia", "Christen", "Nguyen", "Watford", "Hurwitz", "Owens", "Friedland", "Goodwin", "Hug",
                "Schroeder", "Farris", "Pregerson", "Nelson", "Canby", "Noonan", "Leavy", "Trott", "Fernandez", "Kleinfeld",
                "Hawkins", "Silverman", "Fisher"],
                
        "10th": ["Tymkovich", "Kelly", "Briscoe", "Lucero", "Hartz", "Gorsuch", "Holmes", "Matheson", "Bacharach", "Phillips",
                 "McHugh", "Moritz", "McKay", "Seymour", "Porfilio", "Anderson", "Baldock", "Brorby", "Ebel", "Murphy", "O'Brien"],
#         there are two judges named Carnes: Edward Earl Carnes and Julie E. Carnes         
        "11th": ["Carnes", "Tjoflat", "Hull", "Marcus", "Wilson", "Pryor", "Martin", "Jordan", "Rosenbaum", "E. Carnes", "Pryor",
                 "Hill", "Fay", "Kravitch", "Anderson", "Edmondson", "Cox", "Dubina", "Black"]
    }

    agency_regex = {
        "Petition.{,3}?for.{,3}?Rehearing": "rehearing",
        "Board.{0,3}?of.{,3}Immigration.{,3}Appeals": "immigration appeals",
        "Benefits.{,3}?Review.{,3}?Board": "benefits review",
        "Environmental.{,3}?Protection.{,3}?Agency": "epa",
        "Tax.{,3}?Court": "tax court",
        "Federal.{,3}?Energy.{,3}?Regulatory": "ferc",
        "Federal.{,3}?Communications.{,3}?Commission": "fcc",
        "National.{,3}?Labor.{,3}?Relations": "nlrb",
        "Federal.{,3}?Election.{,3}?Commission": "fec",
        "Department.{,3}?of.{,3}?Transportation": "dept_transportation",
        "Surface.{,3}?Transportation.{,3}?Board": "stb",
        "Federal.{,3}?Mine.{,3}?Safety": "fmshrc",
        "Nuclear.{,3}?Regulatory.{,3}?Commission": "nrc",
        "Federal.{,3}?Aviation.{,3}?Administration": "faa",
        "Federal.{,3}?Trade.{,3}?Commission": "ftc",
        "Federal.{,3}?Labor.{,3}?Relations": "flra",
        "Washington.{,3}?Metropolitan.{,3}?Area.{,3}?Transit": "wmatc",
        "United.{,3}?States.{,3}?Postal": "usps",
        "Department.{,3}?of.{,3}?Agriculture": "dept_agriculture",
        "Department.{,3}?of.{,3}?Energy": "dept_energy",
        "Department.{,3}?of.{,3}?Commerce": "dept_commerce",
        "Department.{,3}?of.{,3}?Justice": "dept_justice",
        "Department.{,3}?of.{,3}?the.{,3}?Interior": "dept_interior",
        "Department.{,3}?of.{,3}?Homeland.{,3}?Security": "dept_homeland",
        "Transportation.{,3}?Security.{,3}?Administration": "tsa",
        "Internal.{,3}?Revenue.{,3}?Service": "irs",
        "Health.{,3}?and.{,3}?Human": "hhs",
        "Drug.{,3}?Enforcement.{,3}?Administration": "dea",
        "Food.{,3}?and.{,3}?Drug": "fda",
        "Immigration.{,3}?and.{,3}?Naturalization": "ins",
        "Federal.{,3}?Housing.{,3}?Administration": "fha",
        "Office.{,3}?of.{,3}?Thrift.{,3}?Supervision": "ots",
        "Federal.{,3}?Maritime.{,3}?Commission": "fmc",
        "Writ.{,3}?of.{,3}?Prohibition": "prisons",
        "Occupational.{,3}?Safety.{,3}?and.{,3}?Health": "osha",
        "Railroad.{,3}?Retirement.{,3}?Board": "rrb",
        "Securities.{,3}?and.{,3}?Exchange": "sec",
        "Commodities.{,3}?Future(s)?.{,3}?Trading": "cftc",
        "Federal.{,3}?Deposit.{,3}?Insurance": "fdic",
        "Board.{,3}?of.{,3}?Governors.{,3}?of.{,3}?the.{,3}?Federal.{,3}?Reserve": "federal_reserve",
        "Librarian.{,3}?of.{,3}?Congress": "loc",
        "Department.{,3}?of.{,3}?State": "dept_state",
        "Mine.{,3}?Safety.{,3}?and.{,3}?Health": "msha",
        "Copyright.{,3}?Royalty.{,3}?Board": "crb",
        "Court.{,3}?of.{,3}?Military.{,3}?Commission.{,3}?Review": "commission_review",
    }

    agency_abbreviation_regex = {
        "\sDEA\s": "dea",
        "\sEPA\s": "epa",
        "\sFERC\s": "ferc",
        "\sFCC\s": "fcc",
        "\sNLRB\s": "nlrb",
    }

    disposition_regex = {
        ".{,100}we.{,15}?\s*(?<!would)(?<!would )affirm.{,100}": "affirmed",
        ".{,100}we.{,15}?\s*(?<!would)(?<!would )reverse.{,100}": "reversed",
        ".{,100}we.{,15}?\s*(?<!would)(?<!would )remand.{,100}": "remanded",
        ".{,100}we.{,15}?\s*(?<!would)(?<!would )vacate.{,100}": "vacated",
        ".{,100}we.{,15}?\s*(?<!would)(?<!would )dismiss.{,100}": "dismissed",

        ".{,100}(is|are|be).{,3}?\s*affirmed\..{,100}": "affirmed",
        ".{,100}(is|are|be).{,3}?\s*reversed\..{,100}": "reversed",
        ".{,100}(is|are|be).{,3}?\s*remanded\..{,100}": "remanded",
        ".{,100}(is|are|be).{,3}?\s*vacated\..{,100}": "vacated",
        ".{,100}(is|are|be).{,3}?\s*dismissed\..{,100}": "dismissed",

        ".{,100}the.{,3}?\s*petition(s)?.{,15}?\s*[^\.]*(is|are|be).{,15}?\s*denied.{,100}": "petition denied",
        ".{,100}the.{,3}?\s*petition(s)?.{,15}?\s*[^\.]*(is|are|be).{,15}?\s*dismissed.{,100}": "dismissed",
        ".{,100}the.{,3}?\s*petition(s)?.{,15}?\s*[^\.]*(is|are|be).{,15}?\s*granted.{,100}": "petition granted",
        ".{,100}we.{,15}?\s*grant.{,25}\s*petition.{,100}": "petition granted",
        ".{,100}we.{,15}?\s*deny.{,25}\s*petition.{,100}": "petition denied",

        ".{,100}we.{,15}?\s*dismiss.{,25}\s*petition.{,100}": "dismissed",
        ".{,100}petition.*?must.{,3}?\s*be.{,3}?\s*dismissed.{,100}": "dismissed",

        ".{,100}(judgment|ruling(s)?|decision(s)?)[^\.]{,100}(is|are).{,3}?\s*affirmed(?!.{,3}?\s*in.{,3}?\s*part).{,100}": "affirmed",
        ".{,100}(judgment|ruling(s)?|decision(s)?)[^\.]{,100}(is|are).{,3}?\s*reversed(?!.{,3}?\s*in.{,3}?\s*part).{,100}": "reversed",

        ".{,100}affirmed.{,3}?\s*in.{,3}?\s*part.{,100}": "affirmed in part",
        ".{,100}reversed.{,3}?\s*in.{,3}?\s*part.{,100}": "reversed in part",
        ".{,100}denied\s*in\s*part.{,100}": "denied in part",
        ".{,100}dismissed\s*in\s*part.{,100}": "dismissed in part",

        ".{,100}and.{,3}?\s*remanded.{,3}?\s*for.{,3}?\s*further.{,3}?\s*proceedings.{,100}": "remanded",
        ".{,100}the.{,3}?\s*case.{,3}?\s*is.{,3}?\s*remanded.{,100}": "remanded",

        ".{,100}we.{,15}?\s*affirm{,3}?\s*the{,25}?\s*(judgment|ruling(s)?|decision(s)?).{,100}": "affirmed",
        ".{,100}we.{,15}?\s*reverse{,3}?\s*the{,25}?\s*(judgment|ruling(s)?|decision(s)?).{,100}": "reversed",

        ".{,100}we.{,3}?\s*enforce.{,3}?\s*the.{,25}\s*order.{,100}": "affirmed",
        ".{,100}partially.{,3}?\s*enforce.{,3}?\s*the.{,25}\s*order.{,100}": "affirmed in part",
        ".{,100}we.{,3}?\s*set.{,3}?\s*the.{,25}\s*order.{,3}?\s*aside.{,100}": "vacated",
        ".{,100}dismiss.{,3}?\s*as.{,3}?\s*moot.{,100}": "dismissed as moot",
        ".{,100}we.{,3}?\s*certify.{,20}?\s*questions.{,100}": "certified to another court",
        ".{,100}appeals.{,3}?\s*are.{,15}?\s*dismissed.{,100}": "dismissed",
    }

    disposition_regex_case_sensitive = {
        ".{,100}Affirmed\..{,100}": "affirmed",
        ".{,100}Reversed\..{,100}": "reversed",
        ".{,100}Dismissed\..{,100}": "dismissed",
        ".{,100}Appeal dismissed\..{,100}": "dismissed",
        ".{,100}Vacated\..{,100}": "vacated",
        ".{,100}Remanded\..{,100}": "remanded",
        ".{,100}Denied\..{,100}": "petition denied",
        # add more options
        ".{,100}AFFIRMED": "affirmed",
        ".{,100}REVERSED": "reversed",
        ".{,100}DISMISSED": "dismissed",
        ".{,100}VACATED": "vacated",
        ".{,100}REMANDED": "remanded",

    }

    def __init__(self, session, circuit):
        self.session = session
        # connect the python and mysql, and start a new session.
        self.court = session.query(Court).filter(Court.name == circuit).first()
        if not self.court:
            self.court = Court()
            self.court.name = circuit
            session.add(self.court)
            session.commit()
            session.refresh(self.court)

        self.pdf_extractors = {
            "1st": self._extract_pdf_1st,
            "2nd": self._extract_pdf_2nd,
            "3rd": self._extract_pdf_3rd,
            "4th": self._extract_pdf_4th,
            "5th": self._extract_pdf_5th,
            "6th": self._extract_pdf_6th,
            "7th": self._extract_pdf_7th,
            "8th": self._extract_pdf_8th,
            "9th": self._extract_pdf_9th,
            "10th": self._extract_pdf_10th,
            "11th": self._extract_pdf_11th,
            "DC": self._extract_pdf_dc,
        }

    def extract_metadata(self, xml_file):
        md = {}
        md = Metadata() # class instantiation: for case information

        # read the file
        text = xml_file.read()

        # strip out the namespace, which we don't need
        text = text.replace('xmlns="http://www.loc.gov/mods/v3"', '')

        # parse the xml
        root = etree.fromstring(text)

        ##md.date_issued = root.xpath('//subTitle/following::originInfo/dateIssued')[
        ##    0].text # comment: can we just use //dateIssued?
        md.date_issued = root.xpath('//dateIssued')[0].text # alternative one
        md.case_number = root.xpath('//caseNumber')[0].text
        md.circuit = root.xpath('//courtCircuit')[0].text
        md.title = root.xpath('//title')[0].text
        md.subtitle = root.xpath('//subTitle')[0].text
        md.url = root.xpath('//identifier[@type="uri"]')[0].text
        nos = root.xpath('//natureSuitCode')
        if nos:
            md.nos = nos[0].text
        else:
            md.nos = None

        for party in root.xpath('//party'):
            p_md = {"firstname": party.get("firstName"),
                    "lastname": party.get("lastName"),
                    "role": party.get("role")}

            md.parties.append(p_md)

        return md

    def extract_pdf(self, pdf_file, md): # for the original pdf and metadata

        # open the pdf
        pdf = PdfFileReader(pdf_file)

        # call the circuit-specific extraction method
        if md.circuit in self.pdf_extractors:
            return self.pdf_extractors[md.circuit](pdf, md)
        else:
            print "ERROR: NO EXTRACTOR FOUND"
            return md

    def _extract_pdf_1st(self, pdf, md):
        if pdf.getNumPages() < 3:
            max_pages = pdf.getNumPages()
        else:
            max_pages = 3
        
        # get the total pages of pdf file
        total = pdf.getNumPages()          
        
        # initialize the count
        num_words = 0
            
        # get the all text from pdf file
        for i in range(0, total):
           page = pdf.getPage(i).extractText()
           
           # the number of words in one page
           words = len(page.split())
           
           # the total number of words of opinion
           num_words+= words

        # check the first few pages
        for i in range(0, max_pages):
            page = pdf.getPage(i).extractText()

            # get the lower court
            # first check for administrative agencies
            if not md.lower_court:
                md.lower_court = self._agencies(page)

            # get the lower court
            m = re.search("(APPEALS? FROM|PETITIONS? FOR) ([A-Z\s]+)", page)
            
            if m and not md.lower_court:
                md.lower_court = self._get_court(m.group(2))

            # get the lower court judge
            m = re.search("\[Hon\. (.*?), U\.S\. District Judge(\]|,)", page)
            if m:
                md.lower_court_judge = m.group(1)
                #print md.lower_court_judge

            # get the appellate judges
            m = re.search("Before(.*?)Judges?\.", page)
            if m:
                judges = m.group(1)
                judges = re.sub("Associate|Justice|Circuit|District|Chief| and|Judge(s)?", "", judges)
                judges = re.findall("[A-Z]\w+", judges)
                
                for j in self.circuit_judges["1st"]:
                    if j in judges:
                        md.appellate_judges.append(j)
        
        # get opinion data
        md.opinions = []
        
        m = re.findall(u"([A-Z\s]{6,}).*?by(.*?)Judge\.", md.subtitle)
        if m:             
             authors = m[0][1]
             
             authors = re.sub(u"Chief|Appellate|Judge|and|U\.S\.|Associate|District|Justice\
                 |Supreme|Court|Senior","",authors)
             # clean the author list again 
             authors = re.sub(u"[Oo]f.*designation", "", authors)
             
             for match in m:
                 opinion_data = {
                       "type": match[0].strip().lower(),
                       "length": "Number of Words: {0}".format(num_words),
                       "authors": authors
                 }
                 md.opinions.append(opinion_data)
        
        # need to check again 
        if not md.opinions: 
           m = re.findall(u"SEALED CASE|SEALED OPINION", md.subtitle, re.I)  
           if m:
              opinion_data = {
                    "type": "sealed case",
                    "length": "Number of Words: {0}".format(num_words),
                    "author": "sealed case"
              }
              md.opinions.append(opinion_data)  
           
        # check whether it is published
        publish = re.search(u"[Pp]ublished",md.subtitle, re.I)
        if not publish:
           md.published = False
        
        # get disposition data from the pdf file, and start at the last page
        max_pages = pdf.getNumPages()
        
        # first check the case sensitive 
        for i in range(max_pages-1,0,-1):
            if md.disposition:
               break
            page = pdf.getPage(i).extractText()
            
            for regex, value in self.disposition_regex_case_sensitive.iteritems():
                m = re.search(regex, page)
                if m:
                    md.disposition.append(value)
                    md.disposition_context.append(value + ": " + m.group(0))                    
                
        # more general check using case nonsensitive search
        for i in range(max_pages-1, 0, -1):
            if md.disposition:
               break
            page = pdf.getPage(i).extractText()
            
            
            for regex, value in self.disposition_regex.iteritems():
                m = re.search(regex, page, re.DOTALL | re.I)
                
                if m: 
                     md.disposition.append(value)
                     md.disposition_context.append(value + ": " + m.group(0))
                    
                     
        for attr in dir(md):
          print "{0}: {1}".format(attr, getattr(md, attr))   
                
        if not md.lower_court:
          print "no lower court found"

        if not md.opinions:
          print "opinion authors not found"

        if not md.disposition:
          print "disposition not found"
 
        return md


    def _extract_pdf_2nd(self, pdf, md):


        if pdf.getNumPages() < 3:
            max_pages = pdf.getNumPages()
        else:
            max_pages = 3
            
        # get the total pages of pdf file
        total = pdf.getNumPages()          
        
        # initialize the count
        num_words = 0
            
        # get the all text from pdf file
        for i in range(0, total):
           page = pdf.getPage(i).extractText()
           
           # the number of words in one page
           words = len(page.split())
           
           # the total number of words of opinion
           num_words+= words

        # check the first few pages
        for i in range(0, max_pages):
            page = pdf.getPage(i).extractText()

            # get the lower court
            # first check for administrative agencies
            if not md.lower_court:
                md.lower_court = self._agencies(page)

            # then check for district court
            m = re.search(
                "(Northern|Southern|Eastern|Western|Middle|Central)?.{,3}?District.{,3}?of.{,3}?([A-Z][\w\d\s]+)",
                page)
            if m and not md.lower_court:
                if m.group(1):
                    court = m.group(1) + m.group(2)
                else:
                    court = m.group(2)

                court = re.sub("([A-Z])", " \g<1>", court).strip()
                court = re.sub(" +", " ", court)
                court = re.sub("[^A-Za-z\s]", "", court)

                md.lower_court = self._get_court(court)

            # get the lower court judge
            m = re.search("\([\w\.\s]*([A-Z]\w*?),.{,3}?J(udge)?\.\)", page)
            if m and not md.lower_court_judge:
                md.lower_court_judge = m.group(1)

            # get the appellate judges
            m = re.search("Before:(.{5,}.*?)[\.:\d]", page)
            
            if m:
                potential_judges = m.group(1)
                for judge in self.circuit_judges["2nd"]:
                    if judge.upper() in potential_judges:
                        md.appellate_judges.append(judge)
#       
        # get the list of cases covered by the opinion
        m = re.search("\[.*?-.*?\]", md.subtitle)
        if m:
           case_list = m.group(0)
           m = re.findall("\d\d-\d+", case_list)
           if m:
              # zero pad the second part of each docket number to match the format of other case numbers 
              md.case_list = [case_number[0:3] + case_number[3:].zfill(5) for case_number in m]
           else:
              md.case_list = [md.case_number]
              
        # be default, it's just this case
        else:
            md.case_list = [md.case_number]
        
                              
        # get opinion data
        md.opinions = []
            
        # for the general opinion form     
        m = re.findall("([A-Z]{6,}),(.*?),* by(.*?)FILED\.", md.subtitle)        
        
        if m:
            authors = m[0][2]
            authors = re.sub(",", "",authors)
            
            for match in m:
                opinion_data = {
                    "type": match[0].strip().lower(),
                    "length": "Number of Words: {0}".format(num_words),
                    "authors": authors
                }
                md.opinions.append(opinion_data)
        
        if not md.opinions:
            m = re.findall("([A-Z]{6,}), (.*?) \((.*?)\).*?FILED\.", md.subtitle)
            if m:
               authors = m[0][2]
               authors = re.sub(",", "", authors)
               for match in m:
                   opinion_data = {
                        "type": match[0].strip().lower(),
                        "length": "Number of Words: {0}".format(num_words),
                        "authors": authors
                   }
                   md.opinions.append(opinion_data)        
                   
        if not md.opinions:
           m = re.findall("([A-Z]{6,}), (.*?), per curiam.*?((?:[A-Z]{2,3}[\*\.,\s]*)+).*?FILED\.", md.subtitle)
           if m: 
              authors = m[0][2]
              authors = re.sub(",","",authors)
              
              for match in m:
                  opinion_data = {
                     "type": match[0].strip().lower(),
                     "length":"Number of Words: {0}".format(num_words),
                     "authors": authors
                  }
                  md.opinions.append(opinion_data)
                  
        # per curiam opinion without authors' names
        if not md.opinions:
           m = re.search("per curiam", md.subtitle, re.I)
           if m:
              opinion_data = {
                   "type": "opinion",
                   "length": "Number of Words: {0}".format(num_words),
                   "author": "per curiam"
              }
              md.opinions.append(opinion_data)
        
        # check if a sealed case
        if not md.opinions:
           m = re.search("(sealed case|sealed opinion)", md.subtitle, re.I)
           if m:
              opinion_data = {
                   "type": "sealed case",
                   "length": "Number of Words: {0}".format(num_words),
                   "author": "sealed case"
              }
              md.opinions.append(opinion_data)
           
            
        # no publish data
        md.published = "UNKNOWN"
        
        
        # get disposition from subTitle
        m = re.findall("[A-Z]{6,},(.*?),", md.subtitle)
        
        if m:
           disposition_context = m[0].lower()
           value = re.findall("affirm.{,3}|revers.{,3}|den.{,4}|dismiss.{,3}|vacat.{,3}\
        |remand.{,3}|grant.{,3}|concurring|dissent.{,3}", disposition_context)
           md.disposition_context.append(disposition_context)
           md.disposition.append(value)
           
        for attr in dir(md):
            print "{0}: {1}".format(attr, getattr(md,attr))
        
        if not md.lower_court:
            print "no lower court found"
        
        if not md.opinions:
            print "opinion authors not found"
        
        if not md.disposition_context:
            print "disposition not found"         
 
 
        return md

    def _extract_pdf_3rd(self, pdf, md):

        if pdf.getNumPages() < 3:
            max_pages = pdf.getNumPages()
        else:
            max_pages = 3
            
        # get the total pages of pdf file
        total = pdf.getNumPages()          
        
        # initialize the count
        num_words = 0
            
        # get the all text from pdf file
        for i in range(0, total):
           page = pdf.getPage(i).extractText()
           
           # the number of words in one page
           words = len(page.split())
           
           # the total number of words of opinion
           num_words+= words

        # check the first few pages
        for i in range(0, max_pages):
            page = pdf.getPage(i).extractText()

            # get the lower court
            # first check for administrative agencies
            if not md.lower_court:
                md.lower_court = self._agencies(page)

            # then check for district court
            m = re.search(
                "appeal from.*?(Northern|Southern|Eastern|Western|Middle|Central)?.{,3}?District.{,3}?of.{,3}?([A-Z][\w\d\s]+) \(",
                page, re.I)
            if m and not md.lower_court:
                if m.group(1):
                    court = m.group(1).title() + m.group(2).title()
                else:
                    court = m.group(2).title()

                court = re.sub("([A-Z])", " \g<1>", court).strip()
                court = re.sub(" +", " ", court)
                court = re.sub("[^A-Za-z\s]", "", court)

                md.lower_court = self._get_court(court)
                

            # get the lower court judge
            m = re.search("([A-Z]\w+) District Judge", page)
            if m and not md.lower_court_judge:
                md.lower_court_judge = m.group(1)

            m = re.search("District Judge:.*([A-Z][A-Za-z]+[a-z]) _", page)
            if m and not md.lower_court_judge:
                md.lower_court_judge = m.group(1)

            # get the appellate judges
            if not md.appellate_judges:
                m = re.search("Before:(.{5,}.*?)\(", page, re.I)
                if m:
                    potential_judges = m.group(1)
                    for judge in self.circuit_judges["3rd"]:
                        if judge.upper() in potential_judges:
                            md.appellate_judges.append(judge)
                            
            
            # get opinion data
        md.opinions = []
            
        m = re.findall("(.*?)Coram:(.*),.*Total Pages:.*(\d+)\.*", md.subtitle)
        
        if m:
            # check if pur curiam 
            if "PER CURIAM" in m[0][0]:
               authors = "per curiam"
               
            else:
                
               authors = m[0][1]
               authors = re.sub(",|[Cc]hief|[Jj]udges*|[Cc]ircuit|[Aa]uthoring", "", authors)
            
            for match in m:
                opinion_data = {
                    "type": match[0].strip().lower(),
                    "length": "Pages: {0}, Number of Words: {1}".format(match[2], num_words),
                    "authors": authors,
                }
                md.opinions.append(opinion_data)
        
        # check if published 
        if re.search("NOT PRECEDENTIAL", md.subtitle):
           md.published = False
           print md.published
           
        
        # get disposition  and start from the last page 
        max_pages = pdf.getNumPages()
        
        # first try the case sensitive searches 
        for i in range(max_pages-1, 0, -1):
            if md.disposition:
               break;
            page = pdf.getPage(i).extractText()
            
            for regex, value in self.disposition_regex_case_sensitive.iteritems():
                m = re.search(regex, page)
                if m:
                   md.disposition.append(value)
                   md.disposition_context.append(value + ": " + m.group(0))
                   
        # then try the more general searches 
        if not md.disposition:
           for i in range(max_pages-1, 0, -1):
               page = pdf.getPage(i).extractText()
               
               for regex, value in self.disposition_regex.iteritems():
                   m = re.search(regex, page, re.DOTALL | re.I)
                   if m:
                      md.disposition.append(value)
                      md.disposition_context.append(value + ": " + m.group(0))
        
        for attr in dir(md):
            print "{0}: {1}".format(attr, getattr(md, attr))
            
        if not md.lower_court:
            
            print "no lower court found"

        if not md.opinions:
            print "opinion authors not found"

        if not md.disposition:
            print "disposition not found"
            
        return md

    def _extract_pdf_4th(self, pdf, md):

        if pdf.getNumPages() < 3:
            max_pages = pdf.getNumPages()
        else:
            max_pages = 3
            
        # get the total pages of pdf file
        total = pdf.getNumPages()          
        
        # initialize the count
        num_words = 0
            
        # get the all text from pdf file
        for i in range(0, total):
           page = pdf.getPage(i).extractText()
           
           # the number of words in one page
           words = len(page.split())
           
           # the total number of words of opinion
           num_words+= words

        # check the first few pages
        for i in range(0, max_pages):
            page = pdf.getPage(i).extractText()

            # get the lower court
            # first check for administrative agencies
            if not md.lower_court:
                md.lower_court = self._agencies(page)

            # then check for district court
            m = re.search(
                "appeal(s)? from.*?(Northern|Southern|Eastern|Western|Middle|Central)?.{,3}?district.{,3}?of.{,3}?([A-Z][\w\d\s]+),",
                page, re.I | re.DOTALL)
            if m and not md.lower_court:
                if m.group(2):
                    court = m.group(2).title() + m.group(3).title()
                else:
                    court = m.group(3).title()

                court = re.sub("([A-Z])", " \g<1>", court).strip()
                court = re.sub(" +", " ", court)
                court = re.sub("[^A-Za-z\s]", "", court)

                md.lower_court = self._get_court(court)

                #print md.lower_court

            # get the lower court judge
            m = re.search("([A-Z]\w+)(, Jr\.,|,? II+,|,).{,3}?(Senior |Chief )?District Judge", page, re.DOTALL)
            if m and not md.lower_court_judge:
                md.lower_court_judge = m.group(1)
                print m.group(1)

            # get the appellate judges
            if not md.appellate_judges:
                m = re.search("Before(.{5,}.*?)\.", page, re.I)
                if m:
                    potential_judges = m.group(1)
                    for judge in self.circuit_judges["4th"]:
                        if judge.upper() in potential_judges:
                            md.appellate_judges.append(judge)

                    #print md.appellate_judges
        # get list of cases covered by the opinion
        m = re.search("\[.*?-.*?\]", md.subtitle)
        if m:
           case_list = m.group(0)
           m = re.findall("\d\d-\d+", case_list)
           if m:
              # zero pad the second part of each docket number to match the format of other case numbers
              md.case_list = [case_number[0:3] + case_number[3:].zfill(5) for case_number in m]
           else:
              md.case_list = [md.case_number]
              
        # by default, it's just this case
        else:
            md.case_list = [md.case_number]
                        
        # get opinion data
        md.opinions = []
        
        m = re.findall("Opinion filed by ((?:[A-Z]{2,3}[,\s]*)+).*", md.subtitle)
        if m:
           authors = re.sub(",", "", m[0])
           opinion_data = {
                "type": "opinion",
                "length": "Number of Words: {0}".format(num_words),
                "authors": authors,
           }
           md.opinions.append(opinion_data)
           
        # check if a per curiam opinion
        if not md.opinions:
           m = re.search("PER CURIAM| per curiam", md.subtitle, re.DOTALL|re.I)
           if m:
              opinion_data = {
                  "type": "opinion",
                  "length": "Number of Words: {0}".format(num_words),
                  "authors": "per curiam",
              }
              md.opinions.append(opinion_data)
        
        # get the publish data 
           
        if re.search("UNPUBLISHED", md.subtitle, re.DOTALL|re.I):
           md.published = False   
        
        # get disposition, start at the last page
        max_pages = pdf.getNumPages()
        
        # first try case sensitive searches
        page = pdf.getPage(max_pages-1).extractText() 
        # deal with the capital "A"          
        page = re.sub('Appeal:\s*\d+-\d+.*Doc:.*\d+.*Filed: \d+/\d+/\d+\s*Pg: \d+ of \d+',  "", page)

        # search all the capital characters
        m = re.findall("(?:[A-Z]{2,}\s*)+", page)
        #print m
        m_list = []
        options = []
        for c in m:
           m_list.append(c)   
           
        # remove duplicated disposition from the dictionary 
        for value in self.disposition_regex.itervalues():
            if value not in options:
               options.append(value.upper())
        
        for c in m_list:
            c = str(c)            
            for value in options:
               if c.find(value) != -1 and not md.disposition:
                  md.disposition.append(c)
                  md.disposition_context.append(str(page).rsplit(c,1)[0])

        #try more general searches 
        if not md.disposition:

              for regex, value in self.disposition_regex.iteritems():
                  m = re.search(regex, page, re.DOTALL | re.I)
                  if m:
                     md.disposition.append(value)
                     md.disposition_context.append(value + ": " + m.group(0))

        for attr in dir(md):
            print "{0}: {1}".format(attr, getattr(md, attr))

        if not md.lower_court:
            print "no lower court found"

        if not md.opinions:
            print "opinion authors not found"

        if not md.disposition:
            print "disposition not found"
        
        return md

    def _extract_pdf_5th(self, pdf, md):

        if pdf.getNumPages() < 3:
            max_pages = pdf.getNumPages()
        else:
            max_pages = 3
            
        # get the total pages of pdf file
        total = pdf.getNumPages()          
        
        # initialize the count
        num_words = 0
            
        # get the all text from pdf file
        for i in range(0, total):
           page = pdf.getPage(i).extractText()
           
           # the number of words in one page
           words = len(page.split())
           
           # the total number of words of opinion
           num_words+= words

        md.opinions = []

        # check the first few pages
        for i in range(0, max_pages):
            page = pdf.getPage(i).extractText()

            # get the lower court
            # first check for administrative agencies
            if not md.lower_court:
                md.lower_court = self._agencies(page)

            # then check for district court
            m = re.search(
                "appeal(s)? from.*?(Northern|Southern|Eastern|Western|Middle|Central)?.{,3}?district.{,3}?of.{,3}?([A-Z][\w\d\s]+).{,3}?(US|_)",
                page, re.I | re.DOTALL)
            if m and not md.lower_court:
                if m.group(2):
                    court = m.group(2).title() + m.group(3).title()
                else:
                    court = m.group(3).title()

                court = re.sub("([A-Z])", " \g<1>", court).strip()
                court = re.sub(" +", " ", court)
                court = re.sub("[^A-Za-z\s]", "", court)

                md.lower_court = self._get_court(court)

                #print md.lower_court

            # 5th circuit doesn't report the lower court judge

            # get the appellate judges
            if not md.appellate_judges:
                m = re.search("Before(.{5,}.*?)\.", page, re.I)
                if m:
                    potential_judges = m.group(1)
                    for judge in self.circuit_judges["5th"]:
                        if judge.upper() in potential_judges:
                            md.appellate_judges.append(judge)

                    #print md.appellate_judges
                    
            # get the publish data and opinion data
            # get the publish data
            m = re.search("R\..*47\.5", page)
            if m:
              md.published = False
            # get the opinion data
            
            m = re.search("PER CURIAM", page)
            if m:               
               opinion_data = {
                   "type":"opinion",
                   "length": "Number of Words: {0}".format(num_words),
                   "author":"per curiam",
               }
               md.opinions.append(opinion_data)
       
        # get the disposition data 
        # get the last page 
        max_pages = pdf.getNumPages()
        
        # first try case sensitive search
        for i in range(max_pages-1, 0, -1):
            if md.disposition:
               break
            page = pdf.getPage(i).extractText()
            
            for regex, value in self.disposition_regex_case_sensitive.iteritems():
                m = re.search(regex, page)
                if m:
                   md.disposition.append(value)
                   md.disposition_context.append(value + ": " + m.group(0))
        
        # Then try more general search
        if not md.disposition:
           for i in range(max_pages-1, 0, -1):
               if md.disposition:
                  break
               page = pdf.getPage(i).extractText()
               
               for regex, value in self.disposition_regex.iteritems():
                   m = re.search(regex, page, re.DOTALL | re.I)
                   if m:
                      md.disposition.append(value)
                      md.disposition_context.append(value + ": " + m.group(0))
        
        for attr in dir(md):
            print "{0}: {1}".format(attr, getattr(md, attr))

        if not md.lower_court:
            print "no lower court found"

        if not md.opinions:
            print "opinion authors not found"

        if not md.disposition:
            print "disposition not found"                  
        

        return md

    def _extract_pdf_6th(self, pdf, md):

        if pdf.getNumPages() < 3:
            max_pages = pdf.getNumPages()
        else:
            max_pages = 3
            
        # get the total pages of pdf file
        total = pdf.getNumPages()          
        
        # initialize the count
        num_words = 0
            
        # get the all text from pdf file
        for i in range(0, total):
           page = pdf.getPage(i).extractText()
           
           # the number of words in one page
           words = len(page.split())
           
           # the total number of words of opinion
           num_words+= words


        # check the first few pages
        for i in range(0, max_pages):
            page = pdf.getPage(i).extractText()

            # get the lower court
            # first check for administrative agencies
            if not md.lower_court:
                md.lower_court = self._agencies(page)

            # then check for district court
            m = re.search(
                "appeal(s)? from.*?(Northern|Southern|Eastern|Western|Middle|Central)?.{,3}?district.{,3}?of.{,3}?([A-Z][\w\d\s]+)",
                page, re.I | re.DOTALL)
            if m and not md.lower_court:
                if m.group(2):
                    court = m.group(2).title() + m.group(3).title()
                else:
                    court = m.group(3).title()

                court = re.sub("([A-Z])", " \g<1>", court).strip()
                court = re.sub(" +", " ", court)
                court = re.sub("[^A-Za-z\s]", "", court)

                md.lower_court = self._get_court(court)

                print md.lower_court

            # get the lower court judge
            m = re.search("([A-Z][\w']+)(, Jr\.,|,? II+,|,).{,3}?(Senior |Chief )?District Judge", page, re.DOTALL)
            if m and not md.lower_court_judge:
                md.lower_court_judge = m.group(1)
                #print m.group(1)

            # get the appellate judges
            if not md.appellate_judges:
                m = re.search("Before:(.{5,}.*?)\.", page, re.I)
                if m:
                    potential_judges = m.group(1)
                    for judge in self.circuit_judges["6th"]:
                        if judge.upper() in potential_judges:
                            md.appellate_judges.append(judge)

                    #print md.appellate_judges
                    
        # get the publication data 
        m = re.search("rule 28\(g\)", md.subtitle)
        if m:
           md.published = False
        
        m = re.search("Per Curiam", md.subtitle, re.I)
        if m:
           md.published = False
           
        # get the opinion data 
        md.opinions = []
        
        m = re.findall("Per Curiam(.*)filed.*\. (?:\((\d+) pages\))?", md.subtitle, re.I)
        if m:
           for match in m:
               opinion_data = {
                    "type": match[0].strip().lower(),
                    "length":"Pages: {0}, Number of Words: {1}".format(match[1],num_words),
                    "author": "per curiam",
                }
               md.opinions.append(opinion_data)
        
        m = re.findall("(OPINION) filed.*rule.*?\..*?and(.*)Authoring Circuit Judge.*\. (?:\((\d+) pages\))?", md.subtitle)
        if m:
           for match in m:
               opinion_data = {
                    "type": match[0].strip().lower(),
                    "length": "Pages: {0}, Number of Words: {1}".format(match[2], num_words),
                    "author": match[1],
                }
               md.opinions.append(opinion_data)
        
        if not md.opinions:
           m = re.findall("(OPINION) filed.*rule.*?\..*;(.*)Authoring Circuit Judge.*\. (?:\((\d+) pages\))?", md.subtitle)
           #print m 
           if m:
              for match in m:
                  opinion_data = {
                       "type": match[0].strip().lower(),
                       "length": "Pages: {0}, Number of Words: {1}".format(match[2], num_words),
                       "author": match[1],
                  }
                  md.opinions.append(opinion_data)
        
        if not md.opinions:
            m = re.findall("(.*) filed.*rule.*?(\.|;)(.*)\(AUTHORING\).*\. (?:\((\d+) pages\))?", md.subtitle)
            #print m
            if m:
               for match in m:
                   opinion_data = {
                        "type": match[0].strip().lower(),
                        "length": "Pages: {0}, Number of Words: {1}".format(match[2], num_words),
                        "author": match[1],
                   }
                   md.opinions.append(opinion_data)
        
        # get list of cases covered by the opinion
        m = re.search("\[.*?-.*?\]", md.subtitle)
        if m:
           case_list = m.group(0)
           m = re.findall("\d\d-\d+", case_list)
           if m:
              # zero pad the second part of each docket number to match the format of other case numbers
              md.case_list = [case_number[0:3] + case_number[3:].zfill(5) for case_number in m]
           else:
              md.case_list = [md.case_number]
           
        else:
            md.case_list = [md.case_number]
        
        # get disposition from subtitle 
        m = re.findall(".*filed\s*:(.*?)decision (?:not )?for publication.*\.", md.subtitle)             
        if m:
           for regex, value in self.disposition_regex.iteritems():
               match = re.search(regex, m[0], re.I)
               if match:
                  md.disposition.append(value)
                  md.disposition_context.append(value + ": " + match.group(0))

        # try case sensitive search
        if not md.disposition:
           for regex, value in self.disposition_regex_case_sensitive.iteritems():
               match = re.search(regex, m[0])
               if match:
                  md.disposition.append(value)
                  md.disposition_context.append(value + ": " + match.group(0))                 

        return md

    def _extract_pdf_7th(self, pdf, md):

        if pdf.getNumPages() < 3:
            max_pages = pdf.getNumPages()
        else:
            max_pages = 3
            
        # get the total pages of pdf file
        total = pdf.getNumPages()          
        
        # initialize the count
        num_words = 0
            
        # get the all text from pdf file
        for i in range(0, total):
           page = pdf.getPage(i).extractText()
           
           # the number of words in one page
           words = len(page.split())
           
           # the total number of words of opinion
           num_words+= words

        # check the first few pages
        for i in range(0, max_pages):
            page = pdf.getPage(i).extractText()

            # get the lower court
            # first check for administrative agencies
            if not md.lower_court:
                md.lower_court = self._agencies(page)

            # then check for district court
            m = re.search(
                "appeal(s)? ?from.*?(Northern|Southern|Eastern|Western|Middle|Central)?.{,3}?district.{,3}?of.{,3}?([A-Z][\w\d\s]+)[\,\.]",
                page, re.I | re.DOTALL)
            if m and not md.lower_court:
                if m.group(2):
                    court = m.group(2).title() + m.group(3).title()
                else:
                    court = m.group(3).title()

                court = re.sub("([A-Z])", " \g<1>", court).strip()
                court = re.sub(" +", " ", court)
                court = re.sub("[^A-Za-z\s]", "", court)

                md.lower_court = self._get_court(court)

                #print md.lower_court

            # get the lower court judge
            m = re.search("([A-Z][\w']+)(, Jr\.,|,? II+,|,).{,3}?(Senior |Chief )? Judge", page, re.DOTALL)
            if m and not md.lower_court_judge:
                md.lower_court_judge = m.group(1)
                #print m.group(1)

            # get the appellate judges
            if not md.appellate_judges:
                m = re.search("Before(.{5,}.*?)\.", page, re.I)
                if m:
                    potential_judges = m.group(1)
                    for judge in self.circuit_judges["7th"]:
                        if judge.upper() in potential_judges:
                            md.appellate_judges.append(judge)

                    #print md.appellate_judges

            # alternate appellate judge format
            if not md.appellate_judges:
                matches = re.findall("([A-Z\.\s]+)?, ?(Chief|Circuit) ?Judge", page)
                if matches:
                    for m in matches:
                        for judge in self.circuit_judges["7th"]:
                            if judge.upper() in m[0]:
                                md.appellate_judges.append(judge)

                    #print md.appellate_judges
                    
        # get the publication data
        m = re.findall("(Nonprecedential)", md.subtitle, re.I)

        if m:
           md.published = False
        
        # get the opinion data
        md.opinions = []        
        m = re.findall("Filed opinion of the court by Judge ([A-Za-z].*?)\.", md.subtitle)
        if m:
           for match in m:
               opinion_data = {
                    "type": "opinion",
                    "length": "unknown",
                    "author": match[0],
               }
               md.opinions.append(opinion_data)
               
        # get the disposition data 
        # first try the case sensitive case 
        max_pages = pdf.getNumPages()
        
        for i in range(max_pages-1, 0, -1):
            if md.disposition:
               break
            page = pdf.getPage(i).extractText()
            
            for regex, value in self.disposition_regex_case_sensitive.iteritems():
                m = re.search(regex, page)
                if m:
                   md.disposition.append(value)
                   md.disposition_context.append(value + ": " + m.group(0))
                                     
        # try the more general searches
        if not md.disposition:
           for i in range(max_pages-1, 0, -1):
               if md.disposition:
                  break
                
               page = pdf.getPage(i).extractText()
               
               for regex, value in self.disposition_regex.iteritems():
                   m = re.search(regex, page, re.DOTALL | re.I)
                   if m:
                      md.disposition.append(value)
                      md.disposition_context.append(value + ":" + m.group(0))
                      
                      
        for attr in dir(md):
            print "{0}: {1}".format(attr, getattr(md, attr))

        if not md.lower_court:
            print "no lower court found"

        if not md.opinions:
            print "opinion authors not found"

        if not md.disposition:
            print "disposition not found"    

        return md

    def _extract_pdf_8th(self, pdf, md):

        if pdf.getNumPages() < 3:
            max_pages = pdf.getNumPages()
        else:
            max_pages = 4
            
        # get the total pages of pdf file
        total = pdf.getNumPages()          
        
        # initialize the count
        num_words = 0
            
        # get the all text from pdf file
        for i in range(0, total):
           page = pdf.getPage(i).extractText()
           
           # the number of words in one page
           words = len(page.split())
           
           # the total number of words of opinion
           num_words+= words


        # check the first few pages
        for i in range(0, max_pages):
            page = pdf.getPage(i).extractText()
            
            # get the canonical case name
            if not md.canonical_title:
               m = re.search(u"_[A-Z].*?A[a-z]{6,9},.*?v\.(.*?)A[a-z]{6,9}\.", page)
               if m:
                  print m.group(0)
               

            # get the lower court
            # first check for administrative agencies

            if not md.lower_court:
                md.lower_court = self._agencies(page)

            # then check for district court
            m = re.search(
                "appeal(s)? from.*?(Northern|Southern|Eastern|Western|Middle|Central)?.{,3}?district.{,3}?of.{,3}?([A-Z][\w\d\s]+)",
                page, re.I | re.DOTALL)

            if m and not md.lower_court:
                if m.group(2):
                    court = m.group(2).title() + m.group(3).title()
                else:
                    court = m.group(3).title()

                court = re.sub("([A-Z])", " \g<1>", court).strip()
                court = re.sub(" +", " ", court)
                court = re.sub("[^A-Za-z\s]", "", court)

                md.lower_court = self._get_court(court)

                #print md.lower_court

            # get the lower court judge
            m = re.search("The ?Honorable (.*?)(, (then )?Chief Judge)?, United States District", page, re.DOTALL)
            if m and not md.lower_court_judge:
                md.lower_court_judge = m.group(1)
                #print m.group(1)

            # get the appellate judges
            if not md.appellate_judges:
                m = re.search("Before(.{5,}.*?)\.", page, re.I)
                if m:
                    potential_judges = m.group(1)
                    for judge in self.circuit_judges["8th"]:
                        if judge.upper() in potential_judges:
                            md.appellate_judges.append(judge)
                    #print md.appellate_judges
                    
        # get the publication data 
        m = re.search("UNPUBLISHED", md.subtitle)
        if not m:
           md.published = False
        
        # get covered cases 
        m = re.search("\[.*?-.*?\]", md.subtitle)
        if m:
           case_list = m.group(0)
           m = re.findall("\d\d-\d+", case_list)

           if m:
              # zero pad the second part of each docket number to match the format of the other case numbers
              md.case_list = [case_number[0:3] + case_number[3:].zfill(5) for case_number in m]
           else:
              md.case_list = [md.case_number]
              
        # the opinion data
        md.opinions = []
        
        m = re.findall("OPINION FILED by (.*?), (?:Authoring Judge )?.*\.*", md.subtitle)
        if m:
           opinion_data = {
               "type": "opinion",
               "length": "unknown",
               "author": m[0]
            }
           md.opinions.append(opinion_data)
        
        
        if not md.opinions:
           m = re.findall("PER CURIAM", md.subtitle, re.I)
           if m:
              opinion_data = {
                  "type": "opinion",
                  "length": "unknown",
                  "author": "per curiam",
              }
              md.opinions.append(opinion_data)       
        
        if not md.opinions:
           m = re.findall("OPINION FILED - THE COURT:.*\. (.*?), Authoring Judge", md.subtitle)
           if m:
              opinion_data = {
                 "type": "opinion",
                 "length": "unknown",
                 "author": m[0],
               }
              md.opinions.append(opinion_data)
        
        if not md.opinions:
           m = re.findall("OPINION FILED - THE COURT:.*?AUTHORING JUDGE:(.*?)\(PUBLISHED|UNPUBLISHED\)", md.subtitle)
           if m:
              opinion_data = {
                 "type": "opinion",
                 "length": "unknown",
                 "author": m[0],
              }
              md.opinions.append(opinion_data)
        
        if not md.opinions:
           print md.subtitle
           
        # get disposition data, starting at the last page
        max_pages = pdf.getNumPages()
        
        # first try the case sensitive searches
        for i in range(max_pages-1, 0, -1):
            if md.disposition:
               break
            page = pdf.getPage(i).extractText()
            
            for regex, value in self.disposition_regex_case_sensitive.iteritems():
                m = re.search(regex, page)
                if m:
                   md.disposition.append(value)
                   md.disposition_context.append(value + ": " + m.group(0))
            
        # try more general searches 
        if not md.disposition:
           for i in range(max_pages-1, 0, -1):
               if md.disposition:
                  break
               page = pdf.getPage(i).extractText()
               
               for regex, value in self.disposition_regex.iteritems():
                   m = re.search(regex, page, re.DOTALL|re.I)
                   if m:
                      md.disposition.append(value)
                      md.disposition_context.append(value + ": " + m.group(0))
                     
                      
#         for attr in dir(md):
#             print "{0}: {1}".format(attr, getattr(md, attr))
# 
#         if not md.lower_court:
#             print "no lower court found"
# 
#         if not md.opinions:
#             print "opinion authors not found"
# 
#         if not md.disposition:
#             print "disposition not found"        

        return md

    def _extract_pdf_9th(self, pdf, md):

        if pdf.getNumPages() < 3:
            max_pages = pdf.getNumPages()
        else:
            max_pages = 3
            
        # get the total pages of pdf file
        total = pdf.getNumPages()          
        
        # initialize the count
        num_words = 0
            
        # get the all text from pdf file
        for i in range(0, total):
           page = pdf.getPage(i).extractText()
           
           # the number of words in one page
           words = len(page.split())
           
           # the total number of words of opinion
           num_words+= words

        
        # the number of pages
        pages = pdf.getNumPages()
        
        # check the first few pages
        for i in range(0, max_pages):
            page = pdf.getPage(i).extractText()
        
            # get the canonical case name 
            if not md.canonical_title:
               m = re.search(u".*?CIRCUIT(.*?Appellant).*(v\..*Appellees*)", page, re.DOTALL)
               if m:
                  case_name = m.group(0)
                  case_name = re.sub(u"No\.\s*\d\d-\d+|CV-\d+-\d+-|No\."," ", case_name)
                  case_name = re.findall("CIRCUIT(.*Appellees*)", case_name)
                  md.canonical_title = case_name[0]
                  
            # get the lower court
            # check for district court 
            m = re.search(u"District Court((.*?)District of ([A-Z].*?))[A-Z][a-z]{,50}", page, re.DOTALL)
            if m and not md.lower_court:
               potential_part = m.group(2).lower()
               courts = m.group(3).lower()
               if courts in ["california", "washington"]:
                  m = re.search("(?<=the )\w+", potential_part)
                  if m:
                     part = m.group(0)
                     courts = " ".join([part, courts])
                     md.lower_court = self._get_court(courts)
               
            # check for administrative agencies
            if not md.lower_court:
               md.lower_court = self._agencies(page)
            
            # search for appellate judge panel
            m = re.search("Before:(.*)Circuit Judges", page)
            if m:
               potential_judges = m.group(1)
               for judge in self.circuit_judges["9th"]:
                   if judge.upper() in potential_judges.upper():
                      md.appellate_judges.append(judge)
            
       # if the lower court wasn't found, try again with abbreviations
        if not md.lower_court:
          for i in range(0, max_pages):
              page = pdf.getPage(i).extractText()
              
              #get the lower court
              #first check for administrative agencies
              if not md.lower_court:
                 md.lower_court = self._agency_abbreviations(page)
        
        # get the publication data
        m = re.search("unpublished|non precedential", md.subtitle, re.I)
        if m:
           md.published = False
        
        # get the opinion data
        md.opinions = []
        
        m = re.search("FILED(.*?)\(.*?\).*Judge:(.*?)Authoring.*", md.subtitle, re.I)
        if m:
           opinion_data = {
               "type": m.group(1).strip().lower(),
               "length": pages,
               "author": m.group(2),
           }
           md.opinions.append(opinion_data)
        
        if not md.opinions:
           m = re.findall("per curiam", md.subtitle, re.I)
           if m:
              opinion_data = {
                   "type": "opinion",
                   "length": pages,
                   "author": "per curiam", 
              }
              md.opinions.append(opinion_data)
              
        if not md.opinions:
           m = re.search("FILED OPINION.*\. (?:Judge )?(.*?)Authoring.*\.", md.subtitle)
           if m:
              opinion_data = {
                   "type": "opinion",
                   "length": pages,
                   "author": m.group(1),
              }
              md.opinions.append(opinion_data)
                   
        # get list of cases covered by the opinion
        m = re.search("\[.*?-.*?\]", md.subtitle)
        if m:
           case_list = m.group(0)
           m = re.findall("\d\d-\d+", case_list)
           if m:
              # zero pad the second part of each docket number to match the format of other case numbers
              md.case_list = [case_number[0:3] + case_number[3:].zfill(5) for case_number in m]
           else:
              md.case_list = [md.case_number]
        
        # by default, it's just the case 
        else:
            md.case_list = [md.case_number]
            
        # get the disposition data, starting at the last page
        max_pages = pdf.getNumPages()
        
        # first try the case sensitive searches
        for i in range(max_pages-1, 0, -1):
            if md.disposition:
               break
            page = pdf.getPage(i).extractText()
            
            for regex, value in self.disposition_regex_case_sensitive.iteritems():
                m = re.search(regex, page)
                if m:
                   md.disposition.append(value)
                   md.disposition_context.append(value + ": " + m.group(0))
                   
        # try the more general searches
        if not md.disposition:
           for i in range(max_pages-1, 0, -1):
               if md.disposition:
                  break
               page = pdf.getPage(i).extractText()
               
               for regex, value in self.disposition_regex.iteritems():
                   m = re.search(regex, page, re.DOTALL|re.I)
                   if m:
                      md.disposition.append(value)
                      md.disposition_context.append(value + ": " + m.group(0))

        for attr in dir(md):
            print "{0}: {1}".format(attr, getattr(md, attr))

        if not md.lower_court:
            print "no lower court found"

        if not md.opinions:
            print "opinion authors not found"

        if not md.disposition:
            print "disposition not found"
 
   
        return md

    def _extract_pdf_10th(self, pdf, md):

        if pdf.getNumPages() < 3:
            max_pages = pdf.getNumPages()
           
        else:
            max_pages = 3
            
        # get the total pages of pdf file
        total = pdf.getNumPages()          
        
        # initialize the count
        num_words = 0
            
        # get the all text from pdf file
        for i in range(0, total):
           page = pdf.getPage(i).extractText()
           
           # the number of words in one page
           words = len(page.split())
           
           # the total number of words of opinion
           num_words+= words

        
        # number of pages
        pages = pdf.getNumPages()
        
        # check the first few pages
        for i in range(0, max_pages):
            page = pdf.getPage(i).extractText()
            
            # get the canonical case name 
            if not md.canonical_title:
               m = re.search(".*?CIRCUIT(.*A.{6,8}).*?(v\..*?A[a-z]{6,8})", page, re.DOTALL)
               if m:
                  md.canonical_title = " ". join([m.group(1), m.group(2)])
                  #clean the title again
                  md.canonical_title = re.sub("No\..*?-\d+(?:-\d+)?","", md.canonical_title)
                  
            # get the lower court      
            # check fo administrative agencies
            if not md.lower_court:
               md.lower_court = self._agencies(page)
               #print md.lower_court
            
            # check the district court 
            m = re.search("Appeal from.*?(Eastern|Northern|Western)?.{,3}District.{,3}?of.{,3}?([A-Z][a-z]{,9})", page, re.DOTALL)
            if m and not md.lower_court:
               if m.group(1):
                  court = " ".join([m.group(1), m.group(2)])
               else:
                  court = m.group(2)
               md.lower_court = self._get_court(court)
            
            # if the lower court wasn't found, try again with abbreviations
            if not md.lower_court:
               for i in range(0, max_pages):
                   page = pdf.getPage(i).extractText()
                   
                   #get the lower court
                   #first check for administrative agencies
                   if not md.lower_court:
                      md.lower_court = self._agency_abbreviations(page)
            
        # get the publication data
        m = re.search("unpublished", md.subtitle)
        if m:
           md.published = False
        
        # get the opinion data 
        md.opinions = []
        m = re.findall("\[\d+\].*(published|unpublished).{,3}Judges*(.*?)\. Mandate to issue\.", md.subtitle)

        if m:
           judge = m[0][1]
           m = re.findall("([A-Z][a-z]+), \(?author[a-z]{3}?\)?", judge)
           author = m[0]
           opinion_data = {
                 "type": "opinion",
                 "length": pages,
                 "author": author
           }
           md.opinions.append(opinion_data)
        
        m = re.search("per curiam", md.subtitle, re.I)
        if m:
           opinion_data = {
                "type": "per curiam",
                "length": pages,
                "author": "per curiam",
           }
           md.opinions.append(opinion_data)
        
        # get list of cases covered by the opinion
        m = re.search("\[.*?-.*?\]", md.subtitle)
        if m:
           case_list = m.group(0)
           m = re.findall("\d\d-\d+", case_list)
           if m:
              # zero  pad the second part of each docket number to match the format of other case numbers
              md.case_list = [case_number[0:3] + case_number[3:].zfill(5) for case_number in m]
           else:
              md.case_list = [md.case_number]
        
        # by default, it's just this case
        else:
            md.case_list = [md.case_number]
        
        # get disposition, starting at the last page
        max_pages = pdf.getNumPages()
        
        # first try the case sensitive searches
        for i in range(max_pages-1, 0, -1):
            if md.disposition:
               break
            page = pdf.getPage(i).extractText()
            
            for regex, value in self.disposition_regex_case_sensitive.iteritems():
                m = re.search(regex, page)
                if m:
                   md.disposition.append(value)
                   md.disposition_context.append(value + ": " + m.group(0))
                   
        # failing that try the more general searches
        if not md.disposition:
           for i in range(max_pages-1, 0, -1):
               if md.disposition:
                  break
               
               page = pdf.getPage(i).extractText()
               
               for regex, value in self.disposition_regex.iteritems():
                   m = re.search(regex, page, re.DOTALL | re.I)
                   if m:
                      md.disposition.append(value)
                      md.disposition_context.append(value + ": " + m.group(0))
        
        for attr in dir(md):
            print "{0}: {1}".format(attr, getattr(md, attr))

        if not md.lower_court:
            print "no lower court found"

        if not md.opinions:
            print "opinion authors not found"

        if not md.disposition:
            print "disposition not found"                   

        return md

    def _extract_pdf_11th(self, pdf, md):

        if pdf.getNumPages() < 3:
            max_pages = pdf.getNumPages()
        else:
            max_pages = 3
            
        title = ""
        
        
        # get the total pages of pdf file
        total = pdf.getNumPages()          
        
        # initialize the count
        num_words = 0
            
        # get the all text from pdf file
        for i in range(0, total):
           page = pdf.getPage(i).extractText()
           
           # the number of words in one page
           words = len(page.split())
           
           # the total number of words of opinion
           num_words+= words
        
        # total pages 
        pages = pdf.getNumPages()
        
        # check the first few pages
        for i in range(0, max_pages):
            page = pdf.getPage(i).extractText()
            
            # get the canonical case name 
            if not md.canonical_title: # match the docket number in the title
               m = re.search(u"D\.C\. Docket No\. \d:(?:.*?-)+(.*?,.*?A[a-z]{6,9},).*?(versus).*?([A-Z].*?,.*?A[a-z]{6,9})\.", page)
               if m:
                  for i in range(1,4):
                      title += re.sub(u"l{1,}|\d+", "", m.group(i))
                  md.canonical_title = title.strip()
                  
            # get the lower court
            # check for district court
            m = re.search(u"Appeal from.*(Middle|Southern|Northern) District of (.*?)_", page, re.DOTALL)
            if m and not md.lower_court:
               court = " ".join([m.group(1), m.group(2)])
               md.lower_court = self._get_court(court)
            
            # check fro administrative agencies
            if not md.lower_court:
               md.lower_court = self._agencies(page)
            
            # if the lower court can't be found, try with abbreviation
            if not md.lower_court:
                # get the lower court
                # first check for administrative agencies
                if not md.lower_court:
                    md.lower_court = self._agency_abbreviations(page)
            
            # search for appellate judge panel
            if not md.appellate_judges:
               m = re.search("Before(.*?), Circuit Judges\.", page)
               if m:
                  potential_judges = m.group(1)
                  for judge in self.circuit_judges["11th"]:
                      if judge.upper() in potential_judges.upper():
                         md.appellate_judges.append(judge)
        
        # get the publication data
        m = re.search("Non-Published", md.subtitle)
        if m:
           md.published = False
        
        # get the opinion data
        md.opinions = []
        # in opinion method: consolidated with and also filed in \d\d-\d+
        m = re.search("(Opinion) issued by court.*?Opinion method:(.*?)\.", md.subtitle)
        #print m.group(0)
        if m:
           opinion_data = {
                "type": m.group(2),
                "length": "Number of Words: {0}".format(num_words),
                "author": "unknown",
           }
           md.opinions.append(opinion_data)
           #print md.opinions
        
        # get list of cases covered by the opinion
        m = re.findall("\d+-\d+", md.subtitle)
        if m:
           md.case_list = [case_number[0:3] + case_number[3:].zfill(5) for case_number in m]
        else:
           md.case_list = [md.case_number]   
        
        # get disposition data , starting at the last page
        max_pages = pdf.getNumPages()
        
        # first try the case sensitive searches
        for i in range(max_pages-1, 0, -1):
            if md.disposition:
               break
            page = pdf.getPage(i).extractText()
            
            for regex, value in self.disposition_regex_case_sensitive.iteritems():
                m = re.search(regex, page)
                if m:
                   md.disposition.append(value)
                   md.disposition_context.append(value + ": " + m.group(0))
        
        # try the more general searches
        if not md.disposition:
           for i in range(max_pages-1, 0, -1):
               if md.disposition:
                  break
               page = pdf.getPage(i).extractText()
               
               for regex, value in self.disposition_regex.iteritems():
                   m = re.search(regex, page, re.DOTALL | re.I)
                   if m:
                      md.disposition.append(value)
                      md.disposition_context.append(value + ": " + m.group(0))
        #print md.disposition 
        for attr in dir(md):
            print "{0}: {1}".format(attr, getattr(md, attr))

        if not md.lower_court:
            print "no lower court found"

        if not md.opinions:
            print "opinion authors not found"

        if not md.disposition:
            print "disposition not found"    
                             
        return md

# some problem occurs when run extract.py(DC), because there are some unrecognizable symbols
# in the pdf file

    def _extract_pdf_dc(self, pdf, md):
        if pdf.getNumPages() < 3:
            max_pages = pdf.getNumPages()
        else:
            max_pages = 4
            
        # get the total pages of pdf file
        total = pdf.getNumPages()          
        
        # initialize the count
        num_words = 0
            
        # get the all text from pdf file
        for i in range(0, total):
           page = pdf.getPage(i).extractText()
           
           # the number of words in one page
           words = len(page.split())
           
           # the total number of words of opinion
           num_words+= words

        # check the first few pages
        for i in range(0, max_pages):
            page = pdf.getPage(i).extractText()

            # get the canonical case name
            if not md.canonical_title:
                m = re.search(u"[A-Z][^a-z]*?v\.[^a-z]*", page, re.DOTALL)
                if m:
                    md.canonical_title = m.group(0).strip()
                    # comments: md.canonical_title[-1]?
                    if md.canonical_title[-1] in ["C", "A"]:
                        md.canonical_title = md.canonical_title[:-1]

            # get the lower court
            # check for district court
            m = re.search(u"district.{,3}?court", page, re.I | re.DOTALL)
            if m and not md.lower_court:
                md.lower_court = "dcd"

            # check for administrative agencies
            if not md.lower_court:
                md.lower_court = self._agencies(page)

            # search for appellate judge panel
            if not md.appellate_judges:
                m = re.search(u"Before(.{5,}.*?)Judge(s)?", page, re.I)
                if m:
                    potential_judges = m.group(1)
                    for judge in self.circuit_judges["dc"]:
                        if judge.upper() in potential_judges.upper():
                            md.appellate_judges.append(judge)

        # if the lower court wasn't found, try again with abbreviations
        if not md.lower_court:
            for i in range(0, max_pages):
                page = pdf.getPage(i).extractText()

                # get the lower court
                # first check for administrative agencies
                if not md.lower_court:
                    md.lower_court = self._agency_abbreviations(page)

        # get opinion data
        md.opinions = []

        m = re.findall("([A-Z\s&]{6,}).*?\( ?(\d+) pgs ?\).*?by.*?Judge ([A-Za-z].*?)([^A-Za-z]|$)", md.subtitle)
        if m:
            for match in m:
                opinion_data = {
                    "type": match[0].strip().lower(),
                    "length": "Pages: {0}, Number of Words: {1}".format(match[1], num_words),
                    "author": match[2]
                }
                md.opinions.append(opinion_data)

        m = re.findall("([A-Z\s&]{6,}).*?\( ?Pages: (\d+) ?\).*?by.*?Judge ([A-Za-z].*?)([^A-Za-z]|$)", md.subtitle)
        if m:
            for match in m:
                opinion_data = {
                    "type": match[0].strip().lower(),
                    "length": "Pages: {0}, Number of Words: {1}".format(match[1], num_words),
                    "author": match[2]
                }
                md.opinions.append(opinion_data)

        if not md.opinions:
            m = re.search("([A-Z\s&]{6,}).*?\( ?(\d+) pgs ?\).*?per curiam([^A-Za-z]|$)", md.subtitle, re.I)
            if m:
                opinion_data = {
                    "type": m.group(1).strip().lower(),
                    "length": "Pages: {0}, Number of Words: {1}".format(m.group(2), num_words),
                    "author": "per curiam"
                }
                md.opinions.append(opinion_data)

        if not md.opinions:
            m = re.search("([A-Z\s&]{6,}).*?per curiam.*?\( ?Pages: (\d+) ?\)([^A-Za-z]|$)", md.subtitle, re.I)
            if m:
                opinion_data = {
                    "type": m.group(1).strip().lower(),
                    "length": "Pages: {0}, Number of Words: {1}".format(m.group(2), num_words),
                    "author": "per curiam"
                }
                md.opinions.append(opinion_data)

        if not md.opinions and md.subtitle.startswith("PER CURIAM JUDGMENT"):
            opinion_data = {
                "type": "opinion",
                "length": None,
                "author": "per curiam"
            }
            md.opinions.append(opinion_data)

        if not md.opinions:
            m = re.search("(SEALED CASE|SEALED OPINION).*?\( ?(\d+) pgs ?\)", md.subtitle, re.I)
            if m:
                opinion_data = {
                    "type": "sealed case",
                    "length": "Pages :{0}, Number of Words: {1}".format(m.group(2), num_words),
                    "author": "sealed case"
                }
                md.opinions.append(opinion_data)

        if not md.opinions:
            m = re.search("(SEALED CASE|SEALED OPINION).*?\( ?Pages: (\d+) ?\)", md.subtitle, re.I)
            if m:
                opinion_data = {
                    "type": "sealed case",
                    "length": "Pages :{0}, Number of Words: {1}".format(m.group(2), num_words),
                    "author": "sealed case"
                }
                md.opinions.append(opinion_data)

        # get list of cases covered by the opinion
        m = re.search("\[.*?-.*?\]", md.subtitle)
        if m:
            case_list = m.group(0)
            m = re.findall("\d\d-\d+", case_list)
            if m:
                # zero pad the second part of each docket number to match the format of other case numbers
                md.case_list = [case_number[0:3] + case_number[3:].zfill(5) for case_number in m]
            else:
                md.case_list = [md.case_number]

        # by default, it's just this case
        else:
            md.case_list = [md.case_number]

        # get disposition and publication data, starting at the last page
        max_pages = pdf.getNumPages()

        # first try the case sensitive searches
        for i in range(max_pages - 1, 0, -1):
            if md.disposition:
                break

            page = pdf.getPage(i).extractText()

            if re.search("Rule 36\(d\)", page):
                md.published = False

            for regex, value in self.disposition_regex_case_sensitive.iteritems():
                m = re.search(regex, page)
                if m:
                    md.disposition.append(value)
                    md.disposition_context.append(value + ": " + m.group(0))

        # failing that try the more general searches
        if not md.disposition:
            for i in range(max_pages - 1, 0, -1):
                if md.disposition:
                    break

                page = pdf.getPage(i).extractText()

                for regex, value in self.disposition_regex.iteritems():
                    m = re.search(regex, page, re.DOTALL | re.I)
                    if m:
                        md.disposition.append(value)
                        md.disposition_context.append(value + ": " + m.group(0))

        for attr in dir(md):
            print "{0}: {1}".format(attr, getattr(md, attr))

        if not md.lower_court:
            print "no lower court found"

        if not md.opinions:
            print "opinion authors not found"

        if not md.disposition:
            print "disposition not found"

        return md

    def store_metadata(self, md):

        #return

        # handle lower court
        lower_court = self.session.query(Court).filter(Court.name == md.lower_court).first()
        if not lower_court:
            lower_court = Court()
            lower_court.name = md.lower_court
            self.session.add(lower_court)
            self.session.commit()
            self.session.refresh(lower_court)

        # handle basic case information
        case = Case()
        case.case_number = md.case_number
        case.lower_court_id = lower_court.id
        case.title = md.title
        case.subtitle = md.subtitle
        case.circuit_court_id = self.court.id
        case.url = md.url
        case.date_issued = md.date_issued
        case.nos = md.nos
        case.canonical_title = md.canonical_title

        case.disposition = ",".join(sorted(list(set(md.disposition))))
        case.disposition_context = "\n\n\n".join(md.disposition_context)
        case.published = md.published

        self.session.add(case)
        self.session.commit()
        self.session.refresh(case)

        # handle judges
        for judge_name in md.appellate_judges:
            judge = self.session.query(Judge).filter(Judge.lastname == judge_name).first()
            if not judge:
                judge = Judge()
                judge.court_id = self.court.id
                judge.lastname = judge_name
                self.session.add(judge)
                self.session.commit()
                self.session.refresh(judge)

            cj = self.session.query(CaseJudge).filter(CaseJudge.case_id == case.id) \
                .filter(CaseJudge.judge_id == judge.id).first()

            if not cj:
                cj = CaseJudge()
                cj.case = case
                cj.judge = judge
                self.session.add(cj)
                self.session.commit()

        # handle parties
        for party in md.parties:
            role = self.session.query(Role).filter(Role.name == party["role"]).first()
            if not role:
                role = Role()
                role.name = party["role"]
                self.session.add(role)
                self.session.commit()
                self.session.refresh(role)

            db_party = self.session.query(Party).filter(Party.firstname == party["firstname"]) \
                .filter(Party.lastname == party["lastname"]).first()
            if not db_party:
                db_party = Party()
                db_party.firstname = party["firstname"]
                db_party.lastname = party["lastname"]
                self.session.add(db_party)
                self.session.commit()
                self.session.refresh(db_party)

            # check for existing case_party entry
            cp = self.session.query(CaseParty).filter(CaseParty.case_id == case.id) \
                .filter(CaseParty.party_id == db_party.id) \
                .filter(CaseParty.role_id == role.id).first()

            if not cp:
                cp = CaseParty(role_id=role.id)
                cp.case = case
                cp.party = db_party

                self.session.add(cp)
                self.session.commit()

        # handle opinions
        for opinion in md.opinions:
            judge = self.session.query(Judge).filter(Judge.court_id == self.court.id) \
                .filter(Judge.lastname == opinion["author"]).first()

            if not judge:
                judge = Judge()
                judge.court_id = self.court.id
                judge.lastname = opinion["author"]
                self.session.add(judge)
                self.session.commit()
                self.session.refresh(judge)

            new_opinion = self.session.query(Opinion).filter(Opinion.judge_id == judge.id) \
                .filter(Opinion.opinion_type == opinion["type"]) \
                .filter(Opinion.case_list == str(md.case_list)).first()

            if not new_opinion:
                new_opinion = Opinion()
                new_opinion.judge_id = judge.id
                new_opinion.opinion_type = opinion["type"]
                new_opinion.opinion_length = opinion["length"]

                # HACK used to keep opinions unique
                new_opinion.case_list = str(md.case_list)

                self.session.add(new_opinion)
                self.session.commit()

            co = self.session.query(CaseOpinion).filter(CaseOpinion.case_id == case.id) \
                .filter(CaseOpinion.opinion_id == new_opinion.id).first()
            if not co:
                co = CaseOpinion()
                co.case_id = case.id
                co.opinion_id = new_opinion.id

                self.session.add(co)
                self.session.commit()

    def _get_court(self, s):
        s = s.lower()

        for key, value in self.court_conversion.iteritems():
            if key in s:
                return value

        print s

        return s

    def _agencies(self, page):
        for regex, value in self.agency_regex.iteritems():
        
            if re.search(regex, page, re.DOTALL): 
                return value

        return None

    def _agency_abbreviations(self, page):
        for regex, value in self.agency_abbreviation_regex.iteritems():
            if re.search(regex, page, re.DOTALL):
                return value

        return None


class Metadata():
    def __init__(self):
        self.date_issued = None
        self.case_number = None
        self.circuit = None
        self.title = None
        self.subtitle = None
        self.url = None
        self.nos = None
        
        self.lower_court = None
        self.appellate_judges = []
        self.lower_court_judge = None
        
        self.parties = []
        self.disposition = []
        self.disposition_context = []
        self.published = True
        self.canonical_title = []
        
