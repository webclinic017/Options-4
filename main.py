import numpy as np
import pandas as pd
from pandas_datareader import data as web
from scipy.stats import norm
from datetime import datetime, timedelta
import json
import requests
import pytz

class OptionPricing:
    def __init__(self,r=2.99,stdev=0.4) -> None:
        self.IST = pytz.timezone('US/Eastern')
        self.r = r/100
        self.stdev = stdev

    @staticmethod
    def seconds_to_year(s):
        """
        Converting seconds to years
        """
        return s/(60*60*24*365)


    def d1(self,S, K, T):
        return (np.log(S/K) + ((self.r + (self.stdev**2)/2) * T)) / (self.stdev * np.sqrt(T))
            
    def d2(self,S, K, T):
        return (np.log(S/K) + ((self.r - (self.stdev**2)/2) * T)) / (self.stdev * np.sqrt(T))  

    def CallOptionPrice(self,S, K, T):
        """
        S: Stock Current Price
        K: Strike Price
        r: Risk Free Rate
        stdev: Annulized Volatility
        T: Time
        """
        d_uno = self.d1(S, K, T)
        d_dos = self.d2(S, K, T)
        return (S*norm.cdf(d_uno)) - (K*np.exp(-self.r*T)*norm.cdf(d_dos))


    def PutOptionPrice(self,S, K, T):
        """
        S: Stock Current Price
        K: Strike Price
        r: Risk Free Rate
        stdev: Annulized Volatility
        T: Time
        """
        d_uno = self.d1(S, K, T)
        d_dos = self.d2(S, K, T)
        return (K*np.exp(-self.r*T)*norm.cdf(-d_dos)) - (S*norm.cdf(-d_uno))

    def swing(self,K:float,TYPE:str,S1:float,S2:float,duration:int=30,EXPIRY=None,**kwargs) -> None:
        """
        TYPE: call/put
        duration: in minutes
        pkg = {
            "K":400,
            "TYPE":'put',
            'S1':405,
            'S2':401,
            'duration':60,
            'r':2.99,
            'stdev':0.4
        }
        """
        START = datetime.now(self.IST)
        # print(f"START: {START.strftime('%Y-%m-%d %H:%M:%S')}")

        END = START+timedelta(minutes=duration)
        # print(f"END: {END.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not EXPIRY:
            #### FIND NEXT FRIDAY for Expiry
            wk_day = datetime.now().weekday()
            if wk_day<4:
                t_delta = 4-wk_day
            elif wk_day==4:
                if START.time()>=START.replace(hour=16,minute=0,second=0,microsecond=0).time():
                    t_delta = 7
                else:
                    t_delta = 0
            elif wk_day==5:
                t_delta = 6
            else:
                t_delta = 5

            EXPIRATION = (datetime.now(self.IST)+timedelta(days=t_delta)).replace(hour=16,minute=0,second=0,microsecond=0)
        else:
            EXPIRATION = datetime.strptime(EXPIRY,'%Y-%m-%d').astimezone(self.IST).replace(hour=16) 
        
        # GET TAU DURATION IN YEARS

        ST = EXPIRATION-START
        ST = self.seconds_to_year(ST.total_seconds())
        ET = EXPIRATION-END
        ET = self.seconds_to_year(ET.total_seconds())
        
        
        if TYPE=='call':
            # START
            _s = self.CallOptionPrice(S1, K, ST)
            # END
            _e = self.CallOptionPrice(S2, K, ET)
        else:
            # START
            _s = self.PutOptionPrice(S1, K, ST)
            # END
            _e = self.PutOptionPrice(S2, K, ET)

        print("Expiration:",EXPIRATION.date().strftime("%Y-%m-%d"))
        print("_"*40)
        print(f"Start: ${round(_s,2)} | End: ${round(_e,2)} >> + ${round(_e-_s,2)}")

        print(f"Expected %P/L: {round((_e/_s-1)*100,1)}% In {round((END-START).total_seconds()/60,1)} minutes | {END.strftime('%Y-%m-%d %H:%M:%S')}")


    def option_pricing_analyzer(self,TYPE='call', EXPIRATION='2022-05-13',K=395, S1=390,START='2022-05-12 12:15:26',S2=396,END='2022-05-12 14:00:30',r=2.99,stdev=0.4) -> None:
        """
        EXPIRATION='2022-05-13'
        S1 = 390
        START = '2022-05-12 12:41:00'
        S2 = 394
        END = '2022-05-12 13:10:00'
        TYPE = 'put'
        # STRIKE
        K = 395
        # INTEREST RATE
        r = 2.99 # % 10Year bond Yield


        # =================================================
        log_ret = np.log(1+data.iloc[-10:].pct_change())
        stdev = log_ret.std() * (252**0.5)
        stdev=0.43
        # =================================================
        """

        EXPIRATION = datetime.strptime(EXPIRATION,'%Y-%m-%d').replace(hour=16)

        START = datetime.strptime(START,'%Y-%m-%d %H:%M:%S')
        END = datetime.strptime(END,'%Y-%m-%d %H:%M:%S')
        ST = EXPIRATION-START
        ST = self.seconds_to_year(ST.total_seconds())
        ET = EXPIRATION-END
        ET = self.seconds_to_year(ET.total_seconds())

        r/=100

        if TYPE=='call':
            # START
            _s = self.CallOptionPrice(S1, K, ST)
            # END
            _e = self.CallOptionPrice(S2, K, ET)
        else:
            # START
            _s = self.PutOptionPrice(S1, K, ST)
            # END
            _e = self.PutOptionPrice(S2, K, ET)

        print(f"Start: ${round(_s,2)} | End: ${round(_e,2)} >> + ${round(_e-_s,2)}")

        print(f"Expected %P/L: {round((_e/_s-1)*100,1)}% In {round((END-START).total_seconds()/60,1)} minutes")

if __name__=='__main__':
    pkg = {
        "K":400,
        "TYPE":'call',
        'S1':395,
        'S2':401,
        'duration':60
    }
    o = OptionPricing(r=3,stdev=0.4)
    o.swing(**pkg)
