package crypto;

import javacard.framework.*;

public class crypto extends Applet
{ 
	public static final byte CLA_MonApplet = (byte) 0xB0; 
	
    public static final byte INS_Initialiser_Nom = (byte) 0x01 ; 
    public static final byte INS_Interroger_Nom = (byte) 0x10 ;
     
    public static final byte INS_Initialiser_Matricule = (byte) 0x02; 
	public static final byte INS_Interroger_Matricule = (byte) 0x21;

    public static final byte INS_Initialiser_Prenom = (byte) 0x03;
	public static final byte INS_Interroger_Prenom = (byte) 0x31;
	
    public static final byte INS_Initialiser_Date_Naissance = (byte) 0x04;
	public static final byte INS_Interroger_Date_Naissance = (byte) 0x40;	

    public static final byte INS_Initialiser_UserName = (byte) 0x05;
	public static final byte INS_Interroger_UserName = (byte) 0x0B;
	
	private final static byte INS_verif = (byte) 0x20;

	private final static byte INS_Deb_Pin = (byte) 0x07;
	private final static byte INS_Mod_Pin = (byte) 0x08;
	
	private final static byte esaai_Max = (byte) 0x03;
	private final static byte Taille_Pin = (byte) 0x04;
  
    
	private final static byte init_pin [] = {(byte) '1', (byte) '2', (byte) '3', (byte) '4'};
	private OwnerPIN Pin ;
	
	private final static byte init_pinAdmin [] = {(byte) '1', (byte) '1', (byte) '1', (byte) '1'};
	private OwnerPIN AdminPin ;
	
	private byte [] Matricule; 
	private byte [] Nom;
	private byte [] Prenom;
	private byte [] DateDeNaissance;
	private byte [] UserName; 
	
	private crypto()
	{
		Pin = new OwnerPIN( esaai_Max , Taille_Pin );
		Pin.update(init_pin , (short) 0, (byte) Taille_Pin );
		
		AdminPin = new OwnerPIN( esaai_Max , Taille_Pin );
		AdminPin.update(init_pinAdmin , (short) 0, (byte) Taille_Pin );
		
		Matricule = new byte[(byte) 13] ; 
		Nom = new byte[(byte) 31];
		Prenom = new byte[(byte) 61] ;
		DateDeNaissance = new byte[(byte) 9] ; 
		UserName = new byte[(byte) 21] ; 
	}
	

	public static void install(byte[] bArray, short bOffset, byte bLength) 
	{
		new crypto().register(bArray, (short) (bOffset + 1), bArray[bOffset]);
	}

	public void process(APDU apdu) 
	{
		if (selectingApplet())  
		{
			return;
		}

		byte[] buf = apdu.getBuffer();  
		switch (buf[ISO7816.OFFSET_INS])
		{
		   case INS_Interroger_Matricule:
				 interrogerTab(Matricule,apdu,(short)12); 
			    break;		   
		   case INS_Initialiser_Matricule:
		      	 initialiserTab(Matricule,apdu,(short)12);
			    break;
			   
		   case INS_Interroger_Nom:
				 interrogerTab(Nom,apdu,(short)30); 
			    break;		   
		   case INS_Initialiser_Nom:
		      	 initialiserTab(Nom,apdu,(short)30);
			    break;

		   case INS_Interroger_Prenom:
				 interrogerTab(Prenom,apdu,(short)60); 
			    break;		   
		   case INS_Initialiser_Prenom:
		      	 initialiserTab(Prenom,apdu,(short)60);
			    break;
			 
		   case INS_Interroger_Date_Naissance:
				 interrogerTab(DateDeNaissance,apdu,(short)8); 
			    break;		   
		   case INS_Initialiser_Date_Naissance:
		      	 initialiserTab(DateDeNaissance,apdu,(short)8);
			    break;
		   case INS_verif : 
				 {
				 	verifier(apdu);
				 	return; 
				 }
		   case INS_Interroger_UserName:
				 interrogerTab(UserName,apdu,(short)20); 
			    break;		   
		   case INS_Initialiser_UserName:
		      	 initialiserTab(UserName,apdu,(short)20);
			    break;
		   case INS_Mod_Pin : 
				 { 
					modifier(apdu);
					return;
				 }
		   case INS_Deb_Pin : 
				 { 
				 	debloquer(apdu);
				    return;
				 }	 
		   default:
			     ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
		}
	}

	
	public void interrogerTab(byte [] tab,APDU apdu,short Indice_Fin)
	{
		if (!Pin.isValidated())
		    ISOException.throwIt(ISO7816.SW_SECURITY_STATUS_NOT_SATISFIED);
		byte[] buffer = apdu.getBuffer();
		byte indice; 
		for(indice = 0;indice<= Indice_Fin;indice++)
				buffer[indice]=(byte) tab[indice];
		apdu.setOutgoingAndSend((short)0, (short) Indice_Fin); 
		
	}
	public void initialiserTab(byte [] tab, APDU apdu, short indice_fin)
	{
		if (!Pin.isValidated())
		    ISOException.throwIt(ISO7816.SW_SECURITY_STATUS_NOT_SATISFIED);
		byte[] buffer = apdu.getBuffer();
		byte indice;
	    apdu.setIncomingAndReceive();
	    for(indice = 0;indice<= indice_fin;indice++) 
	    	     tab[indice] =(buffer[ISO7816.OFFSET_CDATA+indice]);  
 
	}	
	private void verifier(APDU apdu) {
		byte[] buf = apdu.getBuffer();
		if (buf[ISO7816.OFFSET_P1] ==0x00)
		{
		    if (buf[ISO7816.OFFSET_LC] != 4)
		      ISOException.throwIt(ISO7816.SW_WRONG_DATA);
		    if (!Pin.check(buf, (short) ISO7816.OFFSET_CDATA, (byte) 4))
		    	if (Pin.getTriesRemaining()==0)
		    		ISOException.throwIt(ISO7816.SW_SECURITY_STATUS_NOT_SATISFIED);
		    	else
		    		ISOException.throwIt((short) (0x68 * 256 + Pin.getTriesRemaining()));
		}else{
			 if (buf[ISO7816.OFFSET_LC] != 4)
		      ISOException.throwIt(ISO7816.SW_WRONG_DATA);
		    if (!AdminPin.check(buf, (short) ISO7816.OFFSET_CDATA, (byte) 4))
		    	if (AdminPin.getTriesRemaining()==0)
		    		ISOException.throwIt(ISO7816.SW_SECURITY_STATUS_NOT_SATISFIED);
		    	else
		    		ISOException.throwIt((short) (0x68 * 256 + AdminPin.getTriesRemaining()));
		}
		
	}

	private void debloquer(APDU apdu) {
		  byte[] buf = apdu.getBuffer();
		  if (!AdminPin.isValidated())
			  ISOException.throwIt(ISO7816.SW_FUNC_NOT_SUPPORTED);
		  if (buf[ISO7816.OFFSET_LC] != 4)
		    ISOException.throwIt(ISO7816.SW_WRONG_DATA);
		  Pin.update(buf, (short) ISO7816.OFFSET_CDATA, (byte) 4);
		  if (!Pin.check(buf, (short) ISO7816.OFFSET_CDATA, (byte) 4))
		    ISOException.throwIt(ISO7816.SW_SECURITY_STATUS_NOT_SATISFIED);			
	}
	private void modifier(APDU apdu) {
		  byte[] buf = apdu.getBuffer();
		  if (!Pin.isValidated())
		    ISOException.throwIt(ISO7816.SW_SECURITY_STATUS_NOT_SATISFIED);
		  if (buf[ISO7816.OFFSET_LC] != 4)
		    ISOException.throwIt(ISO7816.SW_WRONG_DATA);
		  Pin.update(buf, (short) ISO7816.OFFSET_CDATA, (byte) 4);
		  if (!Pin.check(buf, (short) ISO7816.OFFSET_CDATA, (byte) 4))
		    ISOException.throwIt(ISO7816.SW_SECURITY_STATUS_NOT_SATISFIED);
	}	
}
