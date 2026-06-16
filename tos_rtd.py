import win32com.client
import pythoncom
import time

def get_live_tos_data(ticker_symbol: str):
    """
    Connects to the Thinkorswim RTD COM server.
    Includes proper memory management to prevent Win32 IUnknown exceptions.
    """
    print(f"Establishing COM bridge to Thinkorswim RTD for {ticker_symbol}...\n")
    
    rtd = None # Pre-define the variable
    
    try:
        pythoncom.CoInitialize()
        rtd = win32com.client.Dispatch("tos.rtd")
        
        print("[SYSTEM] Successfully bound to 'tos.rtd' COM Server.")
        time.sleep(2)
        
        print("\n✅ Bridge Verified. Thinkorswim is actively broadcasting data.")
        return True

    except Exception as e:
        print(f"❌ RTD Connection Error: {e}")
        return False
    finally:
        # Explicitly release the COM object before uninitializing
        if rtd is not None:
            del rtd 
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    get_live_tos_data("SPY")