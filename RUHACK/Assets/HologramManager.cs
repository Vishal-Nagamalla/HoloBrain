using UnityEngine;

public class HologramManager : MonoBehaviour
{
    public GameObject hologramObject; // The object to be duplicated
    public float rotationSpeed = 50f;
    public float zoomSpeed = 2f;
    private GameObject[] hologramClones = new GameObject[4];

    void Start()
    {
        if (hologramObject == null)
        {
            Debug.LogError("Please assign a 3D object to the Hologram Manager script.");
            return;
        }

        // Create 4 clones of the hologramObject at different angles
        hologramClones[0] = Instantiate(hologramObject, new Vector3(0, 0, 4), Quaternion.Euler(0, 0, 0));
        hologramClones[0].tag = "HologramClone";

        hologramClones[1] = Instantiate(hologramObject, new Vector3(4, 0, 0), Quaternion.Euler(0, 90, 0));
        hologramClones[1].tag = "HologramClone";

        hologramClones[2] = Instantiate(hologramObject, new Vector3(0, 0, -4), Quaternion.Euler(0, 180, 0));
        hologramClones[2].tag = "HologramClone";

        hologramClones[3] = Instantiate(hologramObject, new Vector3(-4, 0, 0), Quaternion.Euler(0, -90, 0));
        hologramClones[3].tag = "HologramClone";
    }

    void Update()
    {
        foreach (GameObject clone in hologramClones)
        {
            if (clone == null) continue;

            // Rotation with Arrow Keys
            if (Input.GetKey(KeyCode.UpArrow))
            {
                clone.transform.Rotate(Vector3.right * rotationSpeed * Time.deltaTime);
            }
            if (Input.GetKey(KeyCode.DownArrow))
            {
                clone.transform.Rotate(Vector3.left * rotationSpeed * Time.deltaTime);
            }
            if (Input.GetKey(KeyCode.LeftArrow))
            {
                clone.transform.Rotate(Vector3.up * rotationSpeed * Time.deltaTime);
            }
            if (Input.GetKey(KeyCode.RightArrow))
            {
                clone.transform.Rotate(Vector3.down * rotationSpeed * Time.deltaTime);
            }

            // Zoom In and Out using + and - keys
            if (Input.GetKey(KeyCode.Equals))  // Equals key for zoom in (+)
            {
                clone.transform.localScale += Vector3.one * zoomSpeed * Time.deltaTime;
            }
            if (Input.GetKey(KeyCode.Minus))  // Minus key for zoom out (-)
            {
                clone.transform.localScale -= Vector3.one * zoomSpeed * Time.deltaTime;
            }
        }
    }
}