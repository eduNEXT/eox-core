import React from 'react';
import { InputText, InputSelect, RadioButtonGroup, RadioButton, TextArea, Button, StatusAlert } from '@edx/paragon'
import { clientRequest } from './client'
import styles from '../css/CourseSettings'


export class CourseSettings extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      findCoursesRegex: '',
      openAlert: false,
      statusAlertMessage: '',
      statusAlertType: '',
      courseList: [],
      courseListTextArea: '',
      advancedSettingList: [],
      detailsSettingList: [],
      hasAdvancedCourseSettings: false,
      settingTypeValue: '',
      detailsSettingValue: '',
      advancedSettingValue: '',
      advancedSettingName: '',
      detailsSettingName: '',
      completedTasks: [],
      failedTasks: []
    }

    this.findCoursesRegexUrl = '/eox-core/management/get_courses';
    this.advancedSettingsUrl = '/settings/advanced/';
    this.detailSettingsUrl = '/settings/details/';

    this.handleChange = this.handleChange.bind(this);
    this.handleFindCoursesSubmit = this.handleFindCoursesSubmit.bind(this);
    this.onCloseAlert = this.onCloseAlert.bind(this);
    this.onSubmitSetting = this.onSubmitSetting.bind(this);
    this.submitNewAdvancedSetting = this.submitNewAdvancedSetting.bind(this);
    this.submitNewDetailSetting = this.submitNewDetailSetting.bind(this);
    this.handleResponse = this.handleResponse.bind(this);
    this.handleCourseListChange = this.handleCourseListChange.bind(this);
  }

  componentDidMount() {
    this.getCourseAdvancedSettings(this.props.courseKey);
    // Adds an empty value at the beginning of the details array.
    if (this.props.detailsFields.length !== 0) {
      const detailsSettingKeys = this.props.detailsFields;
      detailsSettingKeys.unshift('');
      this.setState({
        detailsSettingList: detailsSettingKeys
      });
    }
  }

  handleChange(value, name) {
    // We need to catch a TypeError error due to some Paragon components returns
    // as parameters the key pair value-name and other components returns
    // the generated event on its onChange event.
    // So, we need to capture both in order to update the state values.
    try {
      const elementValue = value.target.value;
      const elementName = value.target.name;
      this.setState({
        [elementName]: elementValue
      });
    } catch (error) {
      if (error instanceof TypeError) {
        if (value !== name) {
          this.setState({
            [name]: value
          });
        }
      } else {
        throw new Error(error);
      }
    }
  }

  handleFindCoursesSubmit(event) {
    event.preventDefault();

    if (this.state.findCoursesRegex === '') {
      this.openStatusAlert('Please, enter a valid course regex.', 'danger')
      return;
    }

    this.setState({
      courseListTextArea: '',
      openAlert: false
    });

    const searchStringScaped = this.state.findCoursesRegex.replace(/[+*]/gm, "%2B");
    const queryUrl = `${this.findCoursesRegexUrl}?search=${searchStringScaped}`;

    clientRequest(
      queryUrl,
      'GET'
    )
    .then(
      res => this.handleResponse(res)
    )
    .then((response) => {
      if (response.status !== 'Failed')
        this.fillCourseList(response);
      else
        this.openStatusAlert(`${response.message}`);
    })
    .catch((error) => {
      this.openStatusAlert(`An error occurred in the course regex searching: ${error.message}`, 'danger');
    });
  }

  onCloseAlert() {
    this.setState({
      openAlert: false
    });
  }

  fillCourseList(response) {
    let courseList = response.courses.join('\n');
    this.setState({
      courseListTextArea: courseList,
      courseList: response.courses
    });
  }

  getCourseAdvancedSettings(courseKey) {

    if (courseKey === '') {
      this.openStatusAlert(`No course key to obtain course advanced settings.`, 'danger');
      return;
    }

    const queryUrl = `${this.advancedSettingsUrl}${this.props.courseKey}`
    clientRequest(
      queryUrl,
      'GET'
    )
    .then(
      res => this.handleResponse(res)
    )
    .then((response) => {
      // Adds an empty value at the beginning of the settings array.
      const advancedSettingKeys = Object.keys(response);
      advancedSettingKeys.unshift('');
      this.setState({
        advancedSettingList: advancedSettingKeys
      });
    })
    .catch((error) => {
      this.openStatusAlert(`An error occurred while getting the course advanced settings: ${error.message}`, 'danger');
    });
  }

  onSubmitSetting() {

    this.setState({
      openAlert: false
    });

    const isValid = this.onSubmitValidator();
    if (isValid) {
      if (!confirm(`Are you sure to change the settings of ${this.state.courseList.length} courses.`))
        return;
      const settingTypeValue = this.state.settingTypeValue;
      if (settingTypeValue === 'details')
        this.submitNewDetailSetting();
      else if (settingTypeValue === 'advanced')
        this.submitNewAdvancedSetting();
    }
  }

  onSubmitValidator() {

    const settingTypeValue = this.state.settingTypeValue;

    if (this.state.courseList.length === 0) {
      this.openStatusAlert('No courses selected to apply the changes.', 'danger');
      return false;
    }

    if (settingTypeValue === '') {
      this.openStatusAlert('Please, select Schedule & details or Advanced settings.', 'danger');
      return false;
    }

    const typeSettingName = Object.getOwnPropertyDescriptor(this.state, `${settingTypeValue}SettingName`);
    const typeMessage = (settingTypeValue === 'details') ? 'Schedule & Details' : 'Advanced settings';

    if (typeSettingName.value === '') {
      this.openStatusAlert(`Please enter a valid ${typeMessage} setting.`, 'danger');
      return false;
    }

    const fieldToCheck = Object.getOwnPropertyDescriptor(this.state, `${settingTypeValue}SettingValue`);
    if (fieldToCheck.value === '') {
      this.openStatusAlert(`Please enter a valid ${typeMessage} value.`, 'danger');
      return false;
    }
    return true;
  }

  submitNewAdvancedSetting() {
    const courses = this.state.courseList;
    const settingName = this.state.advancedSettingName;
    const settingValue = this.state.advancedSettingValue;
    let requetsBody = {};
    this.setState({
      completedTasks: [],
      failedTasks: []
    });

    requetsBody = {
      [settingName]: {
        value: this.convertToType(settingValue)
      }
    };

    for (const courseKey of courses) {
      const queryUrl = `${this.advancedSettingsUrl}${courseKey}`;
      clientRequest(
        queryUrl,
        'POST',
        requetsBody
      )
      .then(
        res => this.handlePostSettingsResponse(res, courseKey)
      )
      .catch((error) => {
        console.log(error.message);
      });
    }
  }

  submitNewDetailSetting() {
    const courses = this.state.courseList;
    this.setState({
      completedTasks: [],
      failedTasks: []
    });

    for (const courseKey of courses) {
      const queryUrl = `${this.detailSettingsUrl}${courseKey}`;
      // We need to get the current settings in order to updated it.
      clientRequest(
        queryUrl,
        'GET'
      )
      .then(
        res => this.handleGetDeatilSettingsResponse(res, courseKey)
      )
      .then((response) => {
        // Deep clone response
        const responseData = JSON.parse(JSON.stringify(response));
        this.postNewDeatilSetting(responseData, queryUrl, courseKey);
      })
      .catch(error => {
        console.error(error.message);
      });
    }
  }

  handleGetDeatilSettingsResponse(response, courseKey) {
    if (response.ok)
      return response.json()

    const failedTaskMessage = `An error ocurred while trying to get the settings of ${courseKey}, ${response.statusText}`;
    const actualFailedTasks = this.state.failedTasks;
    actualFailedTasks.push(<li key={courseKey}>{failedTaskMessage}</li>);

    this.setState({
        failedTasks: actualFailedTasks
    });

    throw new Error(response.statusText);
  }

  postNewDeatilSetting(response, url, courseKey) {
    const settingName = this.state.detailsSettingName;
    const settingValue = this.state.detailsSettingValue;

    response[settingName] = this.convertToType(settingValue);

    clientRequest(
      url,
      'POST',
      response
    )
    .then(res => this.handlePostSettingsResponse(res, courseKey))
    .catch((error) => {
      console.log(error.message);
    });
  }

  handlePostSettingsResponse(response, courseKey) {
    const successesTaskMessage = `Successful change to ${courseKey}`;
    const actualSuccessTasks = this.state.completedTasks;
    const failedTaskMessage = `An error ocurred while trying to post the settings of ${courseKey}, ${response.statusText}`;
    const actualFailedTasks = this.state.failedTasks;

    if (response.ok) {
      response.json().then(json => {
        actualSuccessTasks.push(<li key={courseKey}>{successesTaskMessage}</li>);
        this.setState({
          completedTasks: actualSuccessTasks
        });
      })
      .catch(error => {
        actualFailedTasks.push(<li key={courseKey}>{failedTaskMessage}</li>);
      });
    } else {
      actualFailedTasks.push(<li key={courseKey}>{failedTaskMessage}</li>);
    }

    this.setState({
      failedTasks: actualFailedTasks
    });
  }

  convertToType(value) {
    try {
      const typeValue = JSON.parse(value);

      if (typeof typeValue === 'boolean')
        return typeValue

      if (Array.isArray(typeValue))
        return typeValue

      if (typeof typeValue === 'object')
        return typeValue

      if (typeof typeValue === 'null')
        return null

    } catch (error) {
      if (error instanceof SyntaxError) {
        let dateValue = this.isDateObject(value);
        if (!dateValue)
          return value;
        else
          return dateValue;
      } else {
        throw new Error(error);
      }
    }
    let dateValue = this.isDateObject(value);
    if (!dateValue)
      return value;
    else
      return dateValue;
  }

  isDateObject(value) {
    let dateLocal = new Date(`${value} UTC`);
    if (dateLocal !== null || dateLocal !== undefined || dateLocal.toString() !== 'Invalid Date')
      return dateLocal.toJSON();
    else
      return false
  }

  handleResponse(response) {
    if (response.ok)
      return response.json();

    throw new Error(response.statusText);
  }

  openStatusAlert(message, type) {
    this.setState({
      openAlert: true,
      statusAlertMessage: message,
      statusAlertType: type
    });
  }

  handleCourseListChange(value, name) {
    const courseListRaw = value.split('\n');
    const courseList = courseListRaw.filter(value => {
      if (value !== '')
        return value;
    });
    this.setState({
      courseList: courseList
    });
  }

  render() {
    return (
    <div>
      <div className="row">
        <div className="col-4">
          <form>
            <InputText
              name="findCoursesRegex"
              label="Enter the course regex"
              onChange={this.handleChange}
              value={this.state.findCoursesRegex}
            />
            <Button
              label="Find courses"
              name="find"
              type="submit"
              onClick={this.handleFindCoursesSubmit}
              className={['btn-primary']}
            ></Button>
          </form>
        </div>
        <div className="col-8">
          <TextArea
            name="coursesListValue"
            className={[styles.coursesList]}
            label="Current operation will apply to the following courses:"
            value={this.state.courseListTextArea}
            onChange={this.handleCourseListChange}
          />
        </div>
      </div>
      <div className="row">
        <div className="col-4">
          <RadioButtonGroup
            name="settingTypeValue"
            label="Setting type"
            onChange={this.handleChange}
          >
            <RadioButton value="details">
              Schedule & Details
            </RadioButton>
            <RadioButton value="advanced">
              Advanced Settings
            </RadioButton>
          </RadioButtonGroup>
        </div>
        <div className="col-4">
          <InputSelect
            label="Schedule & Details"
            options={this.state.detailsSettingList}
            name="detailsSettingName"
            onChange={this.handleChange}
          />
        </div>
        <div className="col-4">
          <TextArea
            name="detailsSettingValue"
            label="New value"
            onChange={this.handleChange}
          />
        </div>
      </div>
      <div className="row">
        <div className="col-4">

        </div>
        <div className="col-4">
          <InputSelect
            label="Advanced Settings"
            options={this.state.advancedSettingList}
            name="advancedSettingName"
            onChange={this.handleChange}
          />
        </div>
        <div className="col-4">
          <TextArea
            name="advancedSettingValue"
            label="New value"
            onChange={this.handleChange}
          />
        </div>
      </div>
      <Button
        label="Apply changes"
        name="apply"
        onClick={this.onSubmitSetting}
        className={['btn-primary']}
      ></Button>
      <StatusAlert
        dialog={this.state.statusAlertMessage}
        onClose={this.onCloseAlert}
        open={this.state.openAlert}
        alertType={this.state.statusAlertType}
      />
      <div>
        <h2>Operations complete:</h2>
        <ol>{this.state.completedTasks}</ol>
        <h2>Operations not complete:</h2>
        <ol>{this.state.failedTasks}</ol>
      </div>
    </div>
    );
  }
}
