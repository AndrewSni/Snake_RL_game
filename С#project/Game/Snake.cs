using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.SceneManagement;
using System;
using System.Text;
using System.IO;
using System.IO.Pipes;
using System.Threading;


public class Snake : MonoBehaviour
{

    public List<Transform> Body;
    [Range(0, 3)]
    public float dist_body;
    public GameObject bonePref;
    public GameObject applePref;
    private float speed = 0.02f;
    private float nextActionTime = 0.0f;
    private float period = 0.17f;
    private int action = 0;
    private Transform _transform;
    private GameObject[] objs;
    private int death = 0;
    private int ateApple = 0;
    private Dictionary<int, string> direction = new Dictionary<int, string>(){
        {0, "U"},
        {1, "RU"},
        {2, "R"},
        {3, "RD"},
        {4, "D"},
        {5, "LD"},
        {6, "L"},
        {7, "LU"},
        {8, "U"}
    };
    private int[,] euler = new int[,]
    {
    { 0, 1, 1, 1, 1, -1, -1, -1, 0 },
    { -1, 0, 1, 1, 1, 1, -1, -1, -1 },
    { -1, -1, 0, 1, 1, 1, 1, -1, -1 },
    { -1, -1, -1, 0, 1, 1, 1, 1, -1 },
    { 1, -1, -1, -1, 0, 1, 1, 1, -1 },
    { 1, 1, -1, -1, -1, 0, 1, 1, 1 },
    { 1, 1, 1, -1, -1, -1, 0, 1, 1 },
    { 1, 1, 1, 1, -1, -1, -1, 0, 1 },
    { 0, 1, 1, 1, 1, -1, -1, -1, 0 }
    };
    private string pipeName = "SnakePipe_";
    NamedPipeClientStream pipeClient;

    // Use this for initialization
    void Start()
    {
        _transform = GetComponent<Transform>();
        Instantiate(applePref, new Vector3(UnityEngine.Random.Range(5f, 35f), 0f, UnityEngine.Random.Range(5f, 35f)), Quaternion.identity);
        Application.runInBackground = true;

        pipeClient = new NamedPipeClientStream(".", pipeName, PipeDirection.InOut);
        Debug.Log("Ожидание подключения клиента...");
        pipeClient.Connect();
        Debug.Log("Клиент подключен.");
    }

    // Update is called once per frame
    public void Update()
    {
        if (Time.time > nextActionTime)
        {
            string snakeBody = "";
            int final_event = 0;
            nextActionTime += period;
            Time.timeScale = 0f;
            foreach (var bone in Body)
            {
                if (bone != null)
                {
                    snakeBody = snakeBody + (bone.position.x + 0.001) + "." + (bone.position.z + 0.001) + "/";
                }
            }


            objs = GameObject.FindGameObjectsWithTag("SnakeHead");
            int eulerAngle = Convert.ToInt32(Math.Round(objs[0].transform.eulerAngles.y / 45));
            if (death == -1)
            {
                final_event = death;
            }
            else
            {
                final_event = ateApple;
            }

            objs = GameObject.FindGameObjectsWithTag("Food");

            try
            {

                string response = snakeBody + "//" + objs[0].transform.position.x + "." + objs[0].transform.position.z + "//" + direction[System.Convert.ToInt32(eulerAngle)]+ "//" + final_event;
                byte[] responseBuffer = System.Text.Encoding.ASCII.GetBytes(response);
                pipeClient.Write(responseBuffer, 0, responseBuffer.Length);
            }
            catch (Exception ex)
            {
                Console.WriteLine("Ошибка при обмене данными: " + ex.Message);
            }

            string dataReceived = "";
            try
            {
                byte[] buffer = new byte[10];
                int bytesRead = pipeClient.Read(buffer, 0, buffer.Length);
                dataReceived = System.Text.Encoding.ASCII.GetString(buffer, 0, bytesRead);
                Debug.Log("Получены данные от клиента: " + dataReceived);

            }
            catch (Exception ex)
            {
                Debug.Log("Ошибка при обмене данными: " + ex.Message);
            }

            dataReceived = dataReceived.TrimEnd('\n');
            action = System.Convert.ToInt32(dataReceived);


            action = euler[eulerAngle, action];


            ateApple = 0;
            death = 0;
            Time.timeScale = 1f;
        }
        SnakeMove(_transform.position + _transform.forward * speed);
        _transform.Rotate(0, action, 0);
    }

    void OnApplicationQuit()
    {
        pipeClient.Close();
    }

    private void SnakeMove(Vector3 postion)
    {
        float sqrtDist = dist_body * dist_body;
        Vector3 prevBone = _transform.position;

        foreach (var bone in Body)
        {
            if (bone != null)
            {
                if ((bone.position - prevBone).sqrMagnitude > sqrtDist)
                {
                    var temp = bone.position;
                    bone.position = prevBone;
                    prevBone = temp;
                }
                else
                {
                    break;
                }
            }

        }

        _transform.position = postion;
    }

    public void SnakeAppend()
    {
        var bone = Instantiate(bonePref, new Vector3(100f, 100f, 100f), Quaternion.identity);
        Body.Add(bone.transform);
    }

    void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.tag == "Food")
        {
            Destroy(collision.gameObject);
            Instantiate(applePref, new Vector3(UnityEngine.Random.Range(5f, 35f), 0f, UnityEngine.Random.Range(5f, 35f)), Quaternion.identity);
            SnakeAppend();
            ateApple = 1;

        }
        if ((collision.gameObject.tag == "border") ^ (collision.gameObject.tag == "body"))
        {
            //SceneManager.LoadScene(2);
            int counter = 0;
            objs = GameObject.FindGameObjectsWithTag("body");

            foreach (var bone in objs)
            {
                Destroy(bone);
            }

            objs = GameObject.FindGameObjectsWithTag("SnakeHead");

            foreach (var bone in objs)
            {
                bone.transform.position = new Vector3(UnityEngine.Random.Range(5f, 35f), 0f, UnityEngine.Random.Range(5f, 35f));
                bone.transform.eulerAngles = new Vector3(0f, UnityEngine.Random.Range(0, 360), 0f);
            }

            objs = GameObject.FindGameObjectsWithTag("nearbody");

            foreach (var bone in objs)
            {
                bone.transform.position = new Vector3(100, 0, counter);
                counter++;
            }
            death = -1;
        }
    }
}


//////////////////////////////////////////////////////////////////////////



//if (eulerAngle == actionAngle)
//{
//    action = 0;
//}
//else if (eulerAngle < actionAngle)
//{
//    if ((actionAngle - eulerAngle) > (Math.Abs(actionAngle - eulerAngle + 180)))
//    {
//        action = -1;
//    }
//    else
//    {
//        action = 1;
//    }
//}

//else
//{
//    if ((eulerAngle - actionAngle) > (Math.Abs(eulerAngle - actionAngle + 180)))
//    {
//        action = 1;
//    }
//    else
//    {
//        action = -1;
//    }
//}


//if (eulerAngle < 180)
//{
//    euler = eulerAngle + 180;
//    if (actionAngle > euler)
//        action = -1;
//    else 
//        action = 1;
//}

//else
//{
//    euler = eulerAngle - 180;
//    if (actionAngle > euler)
//        action = 1;
//    else
//        action = -1;
//}

//if (Mathf.Abs(actionAngle - eulerAngle) < 5)
//{
//    action = 0;
//}