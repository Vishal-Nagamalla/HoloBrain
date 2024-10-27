using UnityEngine;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class GestureReceiver : MonoBehaviour
{
    private TcpClient client;
    private NetworkStream stream;
    private string gesture = "";

    void Start()
    {
        ConnectToServer();
        Thread clientThread = new Thread(ListenForData);
        clientThread.Start();
    }

    void Update()
    {
        // Find all GameObjects with the tag "Brain" (or use "HologramClone" if that’s the tag you’re using)
        GameObject[] brainObjects = GameObject.FindGameObjectsWithTag("HologramClone");

        // Apply gestures to each brain object
        foreach (GameObject brain in brainObjects)
        {
            if (gesture == "drag_left")
            {
                brain.transform.Rotate(Vector3.down * Time.deltaTime * 25000f);
            }
            else if (gesture == "drag_right")
            {
                brain.transform.Rotate(Vector3.up * Time.deltaTime * 25000f);
            }
            else if (gesture == "drag_up")
            {
                brain.transform.Rotate(Vector3.left * Time.deltaTime * 25000f);
            }
            else if (gesture == "drag_down")
            {
                brain.transform.Rotate(Vector3.right * Time.deltaTime * 25000f);
            }
            else if (gesture == "zoom_in")
            {
                Debug.Log("Zooming In");
                brain.transform.localScale += Vector3.one * Time.deltaTime * 1000f;
            }
            else if (gesture == "zoom_out")
            {
                Debug.Log("Zooming Out");
                brain.transform.localScale -= Vector3.one * Time.deltaTime * 1000f;
            }

        }

        // Reset gesture after applying it to prevent continuous rotation/zoom
        gesture = "";
    }

    void ConnectToServer()
    {
        client = new TcpClient("localhost", 65432);
        stream = client.GetStream();
    }

    void ListenForData()
    {
        byte[] data = new byte[1024];
        while (true)
        {
            int bytes = stream.Read(data, 0, data.Length);
            gesture = Encoding.ASCII.GetString(data, 0, bytes).Trim();
            Debug.Log("Received Gesture: " + gesture);  // Debug to verify gesture reception
        }
    }

    void OnApplicationQuit()
    {
        stream.Close();
        client.Close();
    }
}