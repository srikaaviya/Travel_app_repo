import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

service_file = str(Path(__file__).resolve().parent.parent)
sys.path.append(service_file)

from Services import ai_service, weather_service

@patch('Services.ai_service.client.chat.completions.create')


def test_ask_gemini(mock_create):

    # Set up the deeply nested fake response that Groq returns
    mock_message = MagicMock()
    mock_message.content = "Here is your packing list!"

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_create.return_value = mock_response
    # Call the function
    result = ai_service.ask_gemini("What should I pack for London?")
    # Verify it pulled out the exact string we mocked
    assert result == "Here is your packing list!"

    # Verify it passed the right prompt to Groq
    args, kwargs = mock_create.call_args
    messages_sent_to_ai = kwargs['messages']
    assert messages_sent_to_ai[0]['content'] == "What should I pack for London?"

# When your code receives the response from the real Groq API, it has to dig four levels deep to find the actual text. It looks like this inside:
# response is an object.
# Inside response, there is a list called choices. It grabs the first item: [0].
# Inside that first choice, there is an object called message.
# Inside that message, there is a string called content (which holds the actual text).

@patch('Services.weather_service.requests.get')
def test_weather_service(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_response.json.return_value = { "list": [{
                "weather": [{"description": "clear sky"}],
                "main": {"temp": 25.5}}
        ]}
    mock_get.return_value = mock_response
    result = weather_service.get_weather("London", "now")
    assert result == ("clear sky", 25)

    args, kwargs = mock_get.call_args
    assert "api.openweathermap.org" in args[0]
    assert "London" in args[0]