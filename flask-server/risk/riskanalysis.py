
class RiskAnalysis():
    def __init__(self):
        pass

    def getSectionRisks(self, section):

        section_of_interest = section
        df = {
        "Disruption Location": ["Section 1", "Section 2", "Section 3", "Section 4", "Section 5", "Section 6", "Section 7", "Section 8"],
        "Alternative Route Efficacy": [3, 5, 5, 5, 9, 8, 8, 10],
        "Alternative Route Diversity": [2, 2, 4, 6, 9, 8, 7, 10],
        "Amount of Traffic Impacted": [1, 1, 3, 4, 7, 7, 7, 8],
        "Overall Risk Level": [6, 8, 12, 15, 25, 23, 22, 28]
        }

        # Plot all criteria as subplots
        criteria = [
            "Alternative Route Efficacy",
            "Alternative Route Diversity",
            "Amount of Traffic Impacted",
            "Overall Risk Level",
        ]

        return df
    
    def getAlternateRouteRisks(self, route_in, route_out):
        data = {
            "Alternative Route": [
                "Military Base", "Tract J", "Insulfoam", "Marathon",
                "ABI", "Transit Area A", "Roger Graves Rd", "Petro Star", "Terminal Rd"
            ],
            "Ease of Implementation": [3, 1, 3, 7, 5, 8, 7, 4, 10],
            "Relative Performance": [2, 3, 3, 4, 7, 8, 6, 10, 10],
            "Route Diversity": [9, 7, 1, 7, 7, 4, 3, 1, 3],
            "Overall Efficacy": [14, 11, 7, 18, 19, 20, 16, 15, 23]
        }

        # Plot all criteria as subplots
        criteria = [
            "Ease of Implementation",
            "Relative Performance",
            "Route Diversity",
            "Overall Efficacy",
        ]

        return data