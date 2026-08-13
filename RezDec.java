import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.security.MessageDigest;
import javax.crypto.Cipher;
import javax.crypto.CipherOutputStream;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

public class RezDec {
    public static File a;

    private static String a(String str) throws Exception{
        String str2 = "";
        for (byte b : MessageDigest.getInstance("MD5").digest(str.getBytes())) {
            String hexString = Integer.toHexString(Integer.parseInt(Integer.toOctalString(b & 255)));
            StringBuilder sb = new StringBuilder();
            sb.append(str2);
            StringBuilder sb2 = sb;
            sb2.append(hexString);
            str2 = sb2.toString();
        }
        return str2;
    }

    public static void a() {
        ByteArrayOutputStream byteArrayOutputStream;
        try {
            byte[] bArr = new byte[4096];
            byteArrayOutputStream = new ByteArrayOutputStream();
                FileInputStream fileInputStream = new FileInputStream(a);
                while (true) {
                    int read = fileInputStream.read(bArr);
                    if (read == -1) {
                        break;
                    }
                    byteArrayOutputStream.write(bArr, 0, read);
                }
                byteArrayOutputStream.close();
                fileInputStream.close();
        } catch (IOException unused2) {
            byteArrayOutputStream = null;
        }
        b(byteArrayOutputStream.toByteArray());
    }

    public static void a(byte[] bArr) {
        try {
            FileOutputStream fileOutputStream = new FileOutputStream(a);
            fileOutputStream.write(bArr);
            fileOutputStream.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] strArr) {
        a = new File(strArr[0]);
        a();
    }

    private static void b(byte[] bArr) {
        ByteArrayOutputStream byteArrayOutputStream;
        Exception e;
        try {
            ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(bArr);
            byteArrayOutputStream = new ByteArrayOutputStream();
            try {
                String substring = a("Armadillo").substring(8, 24);
                IvParameterSpec ivParameterSpec = new IvParameterSpec(substring.getBytes());
                SecretKeySpec secretKeySpec = new SecretKeySpec(substring.getBytes(), "AES");
                Cipher instance = Cipher.getInstance("AES/CBC/PKCS5Padding");
                instance.init(2, secretKeySpec, ivParameterSpec);
                CipherOutputStream cipherOutputStream = new CipherOutputStream(byteArrayOutputStream, instance);
                byte[] bArr2 = new byte[1024];
                while (true) {
                    int read = byteArrayInputStream.read(bArr2);
                    if (read < 0) {
                        break;
                    }
                    cipherOutputStream.write(bArr2, 0, read);
                }
                cipherOutputStream.close();
            } catch (Exception e2) {
                e = e2;
                e.printStackTrace();
                a(byteArrayOutputStream.toByteArray());
            }
        } catch (Exception e3) {
            e = e3;
            byteArrayOutputStream = null;
            e.printStackTrace();
            a(byteArrayOutputStream.toByteArray());
        }
        a(byteArrayOutputStream.toByteArray());
    }
}
