import React from 'react';
import { TextArea, Button, StatusAlert, InputText } from '@edx/paragon'
import { LoadingIconComponent } from './LoadingIcon'
import { clientRequest } from './client'
import styles from '../css/CourseRerun'


export class CourseRerun extends React.Component {

  constructor(props) {
    super(props);

    this.organizationApiUrl = '/organizations';
    this.courseApiUrl = '/course/';

    this.state = {
      courseKey: '',
      organizationList: '',
      organizationListTextArea: '',
      initialOrganizationList: [],
      openAlert: false,
      completedTasks: [],
      failedTasks: [],
      statusAlertMessage: '',
      statusAlertType: '',
      isLoading: false,
      courseRun: '',
      courseName: ''
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.onCloseAlert = this.onCloseAlert.bind(this);
    this.handleOrganizationListChange = this.handleOrganizationListChange.bind(this);
  }

  componentDidMount() {
    this.getOrganizationList();
  }

  handleChange(value, name) {
    if (value !== name) {
      this.setState({
        [name]: value
      });
    }
  }

  getOrganizationList() {
    this.setState({
      isLoading: true
    });

    clientRequest(
      this.organizationApiUrl,
      'GET'
    )
    .then(
      res => this.handleResponse(res)
    )
    .then((response) => {
      this.fillOrganizationList(response);
    })
    .catch((error) => {
      this.openStatusAlert(`An error occurred while getting the organizations list: ${error.message}`, 'danger');
      this.setState({
        isLoading: false
      });
    });
  }

  handleSubmit() {
    const isValid = this.onSubmitValidator();

    if (isValid && confirm(`Rerun ${this.state.courseKey} course into ${this.state.organizationList.length} organizations.`)) {
      this.setState({
        completedTasks: [],
        failedTasks: []
      });
      this.courseKeyExists()
      .then((courseExists) => {
        this.setState({
          isLoading: false
        });
        if (courseExists && this.organizationListExists())
          this.submitRerunCourse();
      });
    }
  }

  submitRerunCourse() {
    let requestTimeOut = 0;
    const courseKeyData = this.getCourseKeyData();

    for (const org of this.state.organizationList) {
      setTimeout(() => {
        this.setState({
          isLoading: true
        });
        const requetsBody = {
          source_course_key: this.state.courseKey,
          org: org,
          number: courseKeyData.number,
          display_name: this.state.courseName,
          run: this.state.courseRun
        }

        clientRequest(
          this.courseApiUrl,
          'POST',
          requetsBody
        )
        .then(
          res => this.handleCourseRerunResponse(res, org)
        )
        .catch((error) => {
          this.openStatusAlert(error.message, 'danger');
          this.setState({
            isLoading: false
          });
        });
      }, requestTimeOut);
      requestTimeOut += this.props.requestTimeOut
    }
  }

  handleCourseRerunResponse(response, organization) {
    const actualSuccessTasks = this.state.completedTasks;
    const actualFailedTasks = this.state.failedTasks;
    const unknownErrorMessage = `An unknown error occurred while tried to rerun a course into ${organization} organization. ${response.statusText}`;

    if (response.ok) {
      response.json()
      .then((jsonResponse) => {
        const destinationCourseKey = Object.getOwnPropertyDescriptor(jsonResponse, 'destination_course_key');
        if (destinationCourseKey) {
          actualSuccessTasks.push(
            <li key={organization}>Rerun completed into {organization} organization.</li>
          );
        } else {
          const errorMessage = `An error occurred while tried to rerun a course into ${organization} organization. ${jsonResponse.ErrMsg}`;
          actualFailedTasks.push(<li key={organization}>{errorMessage}</li>);
        }

        this.setState({
          isLoading: false,
          completedTasks: actualSuccessTasks
        });
      })
      .catch(error => {
        actualFailedTasks.push(<li key={organization}>{unknownErrorMessage}</li>);
      });
    } else {
      actualFailedTasks.push(<li key={organization}>{unknownErrorMessage}</li>);
    }

    this.setState({
      failedTasks: actualFailedTasks,
      isLoading: false
    });
  }

  onSubmitValidator() {
    const courseKey = this.state.courseKey;
    const organizationList = this.state.organizationList;
    const courseRun = this.state.courseRun;
    const courseName = this.state.courseName;

    if (courseKey === '') {
      this.openStatusAlert('Please, enter a valid course key.');
      return false;
    }

    if (organizationList.length === 0) {
      this.openStatusAlert('Please, enter a valid organization name/s.');
      return false;
    }

    if (courseName === '') {
      this.openStatusAlert('Please, enter a valid course name.');
      return false;
    }

    if (courseRun === '') {
      this.openStatusAlert('Please, enter a valid course run.');
      return false;
    }

    return true;
  }

  getCourseKeyData() {
    const courseRegex = /[^/+]+\+([^/+]+)\+([^/?+]+)/gm;
    const courseKey = this.state.courseKey;
    const groups = courseRegex.exec(courseKey);
    const courseData = {
      number: groups[1],
      run: groups[2]
    };

    return courseData;
  }

  async courseKeyExists() {
    const courseKey = this.state.courseKey;
    const queryUrl = `${this.courseApiUrl}${courseKey}`;
    this.setState({
      isLoading: true
    });

    const requestResult = await clientRequest(
      queryUrl,
      'GET'
    )
    .then(
      res => this.handleResponse(res)
    )
    .then((response) => {
      return true;
    })
    .catch((error) => {
      this.openStatusAlert(`The ${courseKey} course key does not exists or a server error has ocurred.`, 'danger');
      this.setState({
        isLoading: false
      });
      return false;
    });

    return requestResult;
  }

  organizationListExists() {
    const organizationList = this.state.initialOrganizationList;
    const actualOrganizationList = this.state.organizationList;
    let unknownOrganization = [];
    let knownOrganization = [];

    for (const org of actualOrganizationList) {
      if (!organizationList.includes(org))
        unknownOrganization.push(org);
      else
        knownOrganization.push(org);
    }

    if (unknownOrganization.length !== 0) {
      const message = `This organization does not exists: ${unknownOrganization.join('\n')}`;
      this.openStatusAlert(message, 'danger');
      return false;
    }

    this.setState({
      organizationList: knownOrganization
    });
    return true;
  }

  fillOrganizationList(response) {
    const organizationList = response.join('\n');
    this.setState({
      organizationListTextArea: organizationList,
      organizationList: response,
      initialOrganizationList: response,
      isLoading: false
    });
  }

  handleResponse(response) {
    if (response.ok)
      return response.json();

    throw new Error(response.statusText);
  }

  onCloseAlert() {
    this.setState({
      openAlert: false
    });
  }

  openStatusAlert(message, type) {
    this.setState({
      openAlert: true,
      statusAlertMessage: message,
      statusAlertType: type
    });
  }

  handleOrganizationListChange(value, name) {
    const organizationListRaw = value.split('\n');
    const organizationList = organizationListRaw.filter(value => {
      if (value !== '')
        return value;
    });
    this.setState({
      organizationList: organizationList
    });
  }

  render() {
    return (
    <div>
      <InputText
        name="courseKey"
        label="Course to rerun:"
        onChange={this.handleChange}
        value={this.state.courseKey}
      />
      <InputText
        name="courseName"
        label="New course name:"
        onChange={this.handleChange}
        value={this.state.courseName}
      />
      <InputText
        name="courseRun"
        label="New course run:"
        onChange={this.handleChange}
        value={this.state.courseRun}
      />
      <TextArea
        name="OrganizationList"
        className={[styles.organizationList]}
        label="Target organizations:"
        value={this.state.organizationListTextArea}
        onChange={this.handleOrganizationListChange}
      />
      <Button
        label="Rerun course."
        onClick={this.handleSubmit}
        className={['btn-primary btn-lg']}
      />
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
      {this.state.isLoading ? <LoadingIconComponent/> : null}
    </div>
    );
  }
}

