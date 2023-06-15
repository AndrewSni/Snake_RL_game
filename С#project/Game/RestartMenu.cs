using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class RestartMenu : MonoBehaviour {

	// Use this for initialization
	public void onPlayHandler()
	{
		SceneManager.LoadScene(1);
	}

	// Update is called once per frame
	public void OnExitHandler()
	{
		Application.Quit();
	}
}
